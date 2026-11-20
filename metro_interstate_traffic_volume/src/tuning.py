"""Tuning báo cáo từ một CSV theo giờ. Chỉ đọc target của 70% train đầu.

Hàm run_tuning chỉ CV, không fit/score validation hoặc test. Lịch sử chỉ dùng
quan sát trước t; cấu hình có C30 yêu cầu cohort đủ history chung cho cả lượt.
Mã tuning lịch sử được giữ ở tuning_exp.py.
"""
import hashlib
import json
import platform
import time
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import ParameterGrid, ParameterSampler, TimeSeriesSplit

from src.evaluation import clip_prediction, regression_metrics
from src.features import add_history_features, has_history
from src.model import CONFIGS, MODEL_NAMES, RANDOM_STATE, SEARCH_SPACE, make_model

N_SPLITS = 3
N_CANDIDATES = 6


@dataclass
class TrainingData:
    """Chỉ giữ train và ngữ cảnh nhiệt độ, không mang validation/test target."""
    frame: pd.DataFrame
    weather_context: pd.DataFrame
    configs: tuple
    metadata: dict


def load_training_data(path=None, *, configs=("A12", "B27")):
    """Đếm timestamp để đặt mốc 70%, sau đó chỉ đọc các dòng train đầu file."""
    path = Path(path) if path is not None else Path(__file__).resolve().parents[1]/"data/preprocessed/hourly_unfilled.csv"
    configs = tuple(configs)
    if not configs or len(set(configs)) != len(configs) or not set(configs) <= CONFIGS.keys():
        raise ValueError("Cần cấu hình A12/B27/C30 duy nhất, không rỗng.")
    times = pd.read_csv(path, usecols=["date_time"], keep_default_na=False).date_time
    times = pd.to_datetime(times, format="%Y-%m-%d %H:%M:%S", errors="raise")
    if times.isna().any() or not times.is_unique or not times.is_monotonic_increasing or not times.eq(times.dt.floor("h")).all():
        raise ValueError("CSV cần timestamp duy nhất, tăng dần, đúng đầu giờ.")
    n_train = len(times)*70//100
    if n_train < 8:
        raise ValueError("Không đủ train để chia CV.")
    numeric = dict(traffic_volume="int64", temp="float64", rain_1h="float64", snow_1h="float64",
                   clouds_all="float64", is_holiday="int8")
    raw = pd.read_csv(path, nrows=n_train, keep_default_na=False, dtype=numeric,
                      na_values={c:[""] for c in numeric}, float_precision="round_trip")
    required = {"date_time", "weather_main", "weather_description", "holiday_name", *numeric}
    if set(raw.columns) != required:
        raise ValueError("Sai schema CSV tiền xử lý.")
    raw["date_time"] = pd.to_datetime(raw.date_time, format="%Y-%m-%d %H:%M:%S", errors="raise")
    if raw.drop(columns=["temp", "rain_1h"]).isna().any().any() or np.isinf(raw[list(numeric)].to_numpy()).any():
        raise ValueError("Train có thiếu ngoài temp/rain hoặc số vô hạn.")
    if not raw.traffic_volume.ge(0).all() or not raw.clouds_all.between(0,100).all() or not raw.is_holiday.isin([0,1]).all():
        raise ValueError("Train có giá trị ngoài miền hợp lệ.")
    featured = add_history_features(raw) if "C30" in configs else raw.copy()
    if "C30" in configs:
        featured = featured.loc[has_history(featured)].copy()
    metadata = dict(input_path=str(path.resolve()), input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    n_total=len(times), n_raw_train=n_train, n_cohort=len(featured),
                    cohort="complete history for all configurations" if "C30" in configs else "all observed train hours",
                    train_end=str(raw.date_time.max()), scope="train CV only; validation/test targets not loaded",
                    weather="same-hour weather assumed available", history="sequential observed past only; mean >=18/24 hours")
    return TrainingData(featured.reset_index(drop=True),raw[["date_time","temp"]].copy(),configs,metadata)


def time_folds(data, n_splits=N_SPLITS):
    """Trả cùng các chỉ số dòng cho mọi mô hình/cấu hình."""
    times = data.frame.date_time
    if not times.is_unique or not times.is_monotonic_increasing:
        raise ValueError("Train không đúng thứ tự.")
    return list(TimeSeriesSplit(n_splits=n_splits).split(data.frame))


def describe_folds(data, n_splits=N_SPLITS):
    """Số mẫu, khoảng lịch và hash timestamp/target của mỗi fold."""
    rows = []
    for number,(fit_idx,score_idx) in enumerate(time_folds(data,n_splits),1):
        fit,score = data.frame.iloc[fit_idx],data.frame.iloc[score_idx]
        row = dict(fold=number,n_fit=len(fit),n=len(score))
        for prefix,part in [("fit",fit),("score",score)]:
            row.update({f"{prefix}_start":str(part.date_time.min()),f"{prefix}_end":str(part.date_time.max()),
                        f"{prefix}_calendar_hours":(part.date_time.max()-part.date_time.min()).total_seconds()/3600+1,
                        f"{prefix}_sha256":hashlib.sha256(pd.util.hash_pandas_object(part[["date_time","traffic_volume"]],index=False).to_numpy().tobytes()).hexdigest()})
        rows.append(row)
    return pd.DataFrame(rows)


def candidate_parameters(name, n_candidates=N_CANDIDATES, random_state=RANDOM_STATE):
    """Lấy đúng số ứng viên không trùng; không âm thầm giảm ngân sách."""
    if name not in SEARCH_SPACE:
        raise ValueError(f"Không hỗ trợ mô hình {name}")
    if not 1 <= n_candidates <= len(ParameterGrid(SEARCH_SPACE[name])):
        raise ValueError(f"Ngân sách không hợp lệ cho {name}; mở rộng search space trước.")
    return list(ParameterSampler(SEARCH_SPACE[name],n_iter=n_candidates,random_state=random_state))


def run_tuning(data, *, model_names=MODEL_NAMES, n_candidates=N_CANDIDATES,
               n_splits=N_SPLITS, output_path=None, progress_callback=None):
    """Tìm tham số theo MAE, cùng folds/ngân sách, xuất một JSON kết quả.

    OOF chỉ lưu cho ứng viên tốt nhất của mỗi cặp model/config để ensemble
    dùng lại. Không tự fit lại model trên toàn train và không chấm holdout.
    """
    names = tuple(model_names)
    if not names or len(set(names)) != len(names):
        raise ValueError("Danh sách mô hình phải duy nhất và không rỗng.")
    bank = {name:candidate_parameters(name,n_candidates) for name in names}
    folds = time_folds(data,n_splits)
    manifest = describe_folds(data,n_splits).to_dict("records")
    observation_rows = []
    for number,(_,score_idx) in enumerate(folds,1):
        observation_rows.extend(dict(fold=number,date_time=str(row.date_time),y_true=float(row.traffic_volume))
                                for row in data.frame.iloc[score_idx].itertuples())
    results = []
    for config in data.configs:
        for name in names:
            candidates,best_predictions,best_key = [],None,None
            for candidate_id,parameters in enumerate(bank[name],1):
                fold_scores,predictions = [],[]
                for number,(fit_idx,score_idx) in enumerate(folds,1):
                    fit,score = data.frame.iloc[fit_idx],data.frame.iloc[score_idx]
                    model = make_model(name,CONFIGS[config],weather_context=data.weather_context).set_params(**parameters)
                    start = time.monotonic()
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter("always")
                        model.fit(fit,fit.traffic_volume)
                        predicted = clip_prediction(model.predict(score))
                    row = dict(**manifest[number-1],**regression_metrics(score.traffic_volume,predicted),
                               seconds=time.monotonic()-start,
                               warnings=sorted({str(w.message) for w in caught}))
                    fold_scores.append(row)
                    predictions.extend(predicted.tolist())
                    if progress_callback:
                        progress_callback(dict(config=config,model=name,candidate=candidate_id,fold=number,MAE=row["MAE"]))
                candidate = dict(candidate=candidate_id,parameters=parameters,folds=fold_scores,
                                 MAE_mean=float(np.mean([r["MAE"] for r in fold_scores])),
                                 RMSE_mean=float(np.mean([r["RMSE"] for r in fold_scores])))
                candidates.append(candidate)
                key = (candidate["MAE_mean"],candidate["RMSE_mean"],candidate_id)
                if best_key is None or key < best_key:
                    best_key,best_predictions = key,predictions
            best = min(candidates,key=lambda r:(r["MAE_mean"],r["RMSE_mean"],r["candidate"]))
            results.append(dict(config=config,model=name,features=CONFIGS[config],best_params=best["parameters"],
                                best_candidate=best["candidate"],MAE_mean=best["MAE_mean"],RMSE_mean=best["RMSE_mean"],
                                candidates=candidates,oof_prediction=best_predictions))
    record = dict(metadata=dict(**data.metadata,n_splits=n_splits,n_candidates=n_candidates,
                               random_state=RANDOM_STATE,selection="mean MAE; RMSE tie-break",prediction_clip_min=0,
                               versions=dict(python=platform.python_version(),pandas=pd.__version__,numpy=np.__version__,sklearn=sklearn.__version__),
                               source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('model.py')]}),
                  folds=manifest,oof_observations=observation_rows,results=results)
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True,exist_ok=True)
        output_path.write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    return record


def results_table(record):
    """Bảng tóm tắt từ file kết quả, không huấn luyện hoặc chấm lại."""
    return pd.DataFrame([dict(config=r["config"],model=r["model"],best_params=r["best_params"],
                              MAE_CV=r["MAE_mean"],RMSE_CV=r["RMSE_mean"],
                              n=len(record["oof_observations"])) for r in record["results"]])


def fit_selected_model(data, result):
    """Fit lại từ tham số đã chọn để dùng validation/ensemble; không tuning lại."""
    if result['config'] not in data.configs or result['features'] != CONFIGS[result['config']]:
        raise ValueError("Kết quả không khớp cấu hình của train.")
    model = make_model(result['model'],result['features'],weather_context=data.weather_context)
    model.set_params(**result['best_params']).fit(data.frame,data.frame.traffic_volume)
    return model
