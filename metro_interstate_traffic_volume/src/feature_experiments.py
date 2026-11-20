"""Đối chứng năm tập đặc trưng bằng một protocol CV cố định.

Các notebook chỉ chọn CONFIG; mọi bước chuẩn bị, fit và chấm dùng chung ở đây.
Không đọc dữ liệu processed đã điền thiếu, không chấm validation hoặc test.
"""
from pathlib import Path
import hashlib
import json
import platform
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

from src.preprocessing import split_by_time, fit_weather_fill, fill_weather
from src.features import (
    CONFIG_A, CONFIG_B, CONFIG_C, WEATHER_NUMERIC_FEATURES,
    WEATHER_GROUP_FEATURES, HISTORY_FEATURES, add_time_features,
    add_weather_features, add_history_features, has_history,
)

CONFIGS = {
    "V1_A12": list(CONFIG_A),
    "V2_numeric16": list(CONFIG_A) + list(WEATHER_NUMERIC_FEATURES),
    "V3_labels23": list(CONFIG_A) + list(WEATHER_GROUP_FEATURES),
    "V4_B27": list(CONFIG_B),
    "V5_C30": list(CONFIG_C),
}
QUESTIONS = {
    "V1_A12": "Đặc trưng lịch tạo mốc sai số như thế nào?",
    "V2_numeric16": "Thêm bốn biến thời tiết số có giảm sai số so với V1 không?",
    "V3_labels23": "Thêm 11 cờ thời tiết có giảm sai số so với V1 không?",
    "V4_B27": "Kết hợp thời tiết số và nhãn có tốt hơn từng nhóm riêng không?",
    "V5_C30": "Thêm lịch sử có giảm sai số so với V4 khi cùng các giờ đánh giá không?",
}
MODEL_PARAMS = dict(n_estimators=400, max_depth=12, min_samples_leaf=5,
                    max_features=1.0, random_state=42, n_jobs=4)
N_SPLITS = 3


def digest(value):
    """Hash metadata theo định dạng thống nhất để ngăn trộn hai protocol."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def frame_hash(frame):
    """Hash cả thứ tự dòng, tên cột và giá trị của một bảng."""
    return hashlib.sha256(
        '|'.join(frame.columns).encode() +
        pd.util.hash_pandas_object(frame, index=False).to_numpy().tobytes()
    ).hexdigest()


def load_protocol(root):
    """Đọc CSV theo giờ từ notebook tiền xử lý, khóa cohort/fold trước khi fit."""
    root = Path(root)
    path = root / "data/preprocessed/hourly_unfilled.csv"
    if not path.is_file():
        raise FileNotFoundError("Chạy notebooks/preprocessing/preprocessing.ipynb để xuất data/preprocessed/hourly_unfilled.csv trước FE.")
    numeric_types = dict(traffic_volume="int64", temp="float64", rain_1h="float64",
                         snow_1h="float64", clouds_all="float64", is_holiday="int8")
    hourly = pd.read_csv(path, keep_default_na=False, dtype=numeric_types,
                         na_values={column: [""] for column in numeric_types},
                         float_precision="round_trip")
    expected = {"date_time", "weather_main", "weather_description", "holiday_name", *numeric_types}
    if set(hourly.columns) != expected:
        raise ValueError("CSV preprocessed sai schema bảng theo giờ; cần chạy lại notebook tiền xử lý.")
    hourly["date_time"] = pd.to_datetime(hourly.date_time, format="%Y-%m-%d %H:%M:%S", errors="raise")
    times = hourly.date_time
    if times.isna().any() or not times.is_unique or not times.is_monotonic_increasing or not times.eq(times.dt.floor("h")).all():
        raise ValueError("CSV cần timestamp duy nhất, tăng dần và đúng đầu giờ.")
    if hourly.drop(columns=["temp", "rain_1h"]).isna().any().any():
        raise ValueError("Chỉ temp/rain_1h được phép thiếu trong bảng bàn giao.")
    if np.isinf(hourly[list(numeric_types)].to_numpy()).any():
        raise ValueError("CSV có giá trị vô hạn.")
    if not hourly.traffic_volume.ge(0).all() or not hourly.clouds_all.between(0, 100).all() or not hourly.is_holiday.isin([0, 1]).all():
        raise ValueError("CSV có target, mây hoặc cờ lễ ngoài miền hợp lệ.")
    if hourly[["rain_1h", "snow_1h"]].lt(0).any().any() or hourly.temp.le(0).any():
        raise ValueError("CSV còn giá trị thời tiết ngoài miền hợp lệ.")
    train = split_by_time(hourly)["train"].reset_index(drop=True)
    featured = add_history_features(add_weather_features(add_time_features(train)))
    cohort = featured.loc[has_history(featured)].reset_index(drop=True)
    folds = list(TimeSeriesSplit(n_splits=N_SPLITS).split(cohort))
    rows = []
    for number, (fit_idx, score_idx) in enumerate(folds, 1):
        fit, score = cohort.iloc[fit_idx], cohort.iloc[score_idx]
        rows.append(dict(
            fold=number, fit_start=fit.date_time.min(), fit_end=fit.date_time.max(),
            score_start=score.date_time.min(), score_end=score.date_time.max(),
            n_fit=len(fit), n=len(score),
            fit_calendar_hours=(fit.date_time.max()-fit.date_time.min()).total_seconds()/3600+1,
            score_calendar_hours=(score.date_time.max()-score.date_time.min()).total_seconds()/3600+1,
            fit_hash=frame_hash(fit[["date_time", "traffic_volume"]]),
            score_hash=frame_hash(score[["date_time", "traffic_volume"]]),
        ))
    manifest = pd.DataFrame(rows)
    source_files = [Path(__file__), *(root / "src" / x for x in
                     ["data.py", "preprocessing.py", "features.py", "data_validation.py"])]
    metadata = dict(
        protocol_version=1, data_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        input_stage="data/preprocessed/hourly_unfilled.csv; cleaning exported before CV, no learned imputation",
        source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
        model="RandomForestRegressor", model_params=MODEL_PARAMS, configs=CONFIGS,
        folds=manifest.to_dict("records"), cohort_hash=frame_hash(cohort[["date_time", "traffic_volume"]]),
        n_train=len(train), n_cohort=len(cohort), min_history=18,
        versions=dict(python=platform.python_version(), numpy=np.__version__,
                      pandas=pd.__version__, sklearn=sklearn.__version__),
        scope="CV inside chronological 70% train only; sequential hourly prediction",
        weather_availability="same-hour weather assumed observed at prediction time",
        cleaning="distinct-value hourly median; 0 K and known rain outlier masked; no stuck-temp mask; CSV holiday by day",
        imputation="fold-train weather statistics; observed backward temp <=6h; month/hour median then overall median; rain median",
        history="exact t-24h/t-168h; mean [t-24h,t), >=18 observations; no target filling",
        selection="mean fold MAE, then mean fold RMSE, then config name",
    )
    protocol_id = digest(metadata)[:16]
    output = root / "notebooks/features/outputs" / protocol_id
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "protocol.json", metadata)
    manifest.to_csv(output / "fold_manifest.csv", index=False)
    return dict(root=root, train=train, featured=featured, cohort=cohort, folds=folds,
                manifest=manifest, metadata=metadata, protocol_id=protocol_id, output=output)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def prepare_fold(train, featured, fit_times, score_times):
    """Học điền thiếu trên fold-train; tạo cùng bảng 30 cột cho mọi phương án.

    Giữ các quan sát thời tiết gốc ngoài cohort làm ngữ cảnh backward-fill.
    Chúng không tham gia fit median. History lấy từ toàn chuỗi quan sát quá khứ,
    không tính lại sau khi bỏ các giờ thiếu lag.
    """
    indexed = train.set_index("date_time", drop=False)
    fit_rows = indexed.loc[fit_times].reset_index(drop=True)
    statistics = fit_weather_fill(fit_rows)
    fit_end = max(fit_times)
    fit_context = train.loc[train.date_time.le(fit_end)].copy()
    score_context = train.loc[train.date_time.gt(fit_end) & train.date_time.le(max(score_times))].copy()
    filled_fit = fill_weather(fit_context, statistics)
    filled_score = fill_weather(score_context, statistics, history=fit_context)
    history = featured.set_index("date_time")[HISTORY_FEATURES]
    matrices = []
    for filled, times in [(filled_fit, fit_times), (filled_score, score_times)]:
        prepared = add_weather_features(add_time_features(filled)).set_index("date_time").loc[times]
        prepared[HISTORY_FEATURES] = history.loc[times]
        matrix = prepared[CONFIG_C].astype("float32")
        if not np.isfinite(matrix.to_numpy()).all():
            raise ValueError("Còn NaN/inf sau chuẩn bị fold; không tự bỏ dòng riêng từng cấu hình.")
        matrices.append(matrix)
    stats_log = dict(
        n=len(fit_rows), fit_start=str(min(fit_times)), fit_end=str(fit_end),
        temp_fallback=float(statistics["temp_fallback"]), rain_median=float(statistics["rain_median"]),
        temp_by_month_hour=[dict(month=int(m), hour=int(h), median=float(v))
                           for (m, h), v in statistics["temp_by_month_hour"].items()],
        fit_matrix_hash=frame_hash(matrices[0].reset_index()),
        score_matrix_hash=frame_hash(matrices[1].reset_index()),
    )
    return matrices[0], matrices[1], stats_log


def run_configuration(context, config):
    """Fit đúng ba RF cùng params, lưu metrics và dự đoán để kiểm toán lại."""
    features = CONFIGS[config]
    output = context["output"] / config
    output.mkdir(exist_ok=True)
    scores, predictions, preprocessing = [], [], []
    cohort = context["cohort"]
    for fold, (fit_idx, score_idx) in enumerate(context["folds"], 1):
        fit, score = cohort.iloc[fit_idx], cohort.iloc[score_idx]
        x_fit, x_score, stats = prepare_fold(context["train"], context["featured"], fit.date_time, score.date_time)
        model = RandomForestRegressor(**MODEL_PARAMS)
        start = time.monotonic()
        model.fit(np.ascontiguousarray(x_fit[features]), fit.traffic_volume.to_numpy())
        predicted = model.predict(np.ascontiguousarray(x_score[features]))
        row = context["manifest"].iloc[fold-1].to_dict()
        row.update(config=config, n_features=len(features),
                   MAE=mean_absolute_error(score.traffic_volume, predicted),
                   RMSE=np.sqrt(mean_squared_error(score.traffic_volume, predicted)),
                   R2=r2_score(score.traffic_volume, predicted), elapsed_seconds=time.monotonic()-start)
        scores.append(row)
        predictions.append(pd.DataFrame(dict(fold=fold, date_time=score.date_time.to_numpy(),
                                            y_true=score.traffic_volume.to_numpy(), y_pred=predicted)))
        preprocessing.append(dict(fold=fold, **stats))
        print(f"{config}, fold {fold}/{N_SPLITS}: MAE={row['MAE']:.3f}, RMSE={row['RMSE']:.3f}", flush=True)
    result = pd.DataFrame(scores)
    result.to_csv(output / "cv_scores.csv", index=False)
    pd.concat(predictions, ignore_index=True).to_csv(output / "oof_predictions.csv", index=False)
    write_json(output / "preprocessing.json", preprocessing)
    write_json(output / "run_manifest.json", dict(protocol_id=context["protocol_id"], config=config,
               features=features, model_params=MODEL_PARAMS, complete=True))
    return result


def compare_configurations(context):
    """Chỉ xếp hạng khi đủ năm run cùng protocol và fingerprint chuẩn bị fold."""
    rows, reference = [], None
    for config, features in CONFIGS.items():
        folder = context["output"] / config
        if not (folder / "run_manifest.json").exists():
            rows.append(dict(config=config, n_features=len(features), status="chưa chạy", n=0))
            continue
        run = json.loads((folder / "run_manifest.json").read_text(encoding="utf-8"))
        assert run["protocol_id"] == context["protocol_id"] and run["model_params"] == MODEL_PARAMS
        assert run["features"] == features and run["complete"]
        scores = pd.read_csv(folder / "cv_scores.csv")
        assert scores.fold.tolist() == [1, 2, 3]
        for key in ["fit_hash", "score_hash", "n_fit", "n"]:
            assert scores[key].tolist() == context["manifest"][key].tolist()
        stats = json.loads((folder / "preprocessing.json").read_text(encoding="utf-8"))
        if reference is None:
            reference = stats
        assert stats == reference, "Khác dữ liệu hoặc preprocessing giữa các cấu hình."
        rows.append(dict(config=config, n_features=len(features), status="đã chạy",
                         MAE_mean=scores.MAE.mean(), MAE_std=scores.MAE.std(ddof=1),
                         RMSE_mean=scores.RMSE.mean(), RMSE_std=scores.RMSE.std(ddof=1),
                         n=int(scores.n.sum())))
    summary = pd.DataFrame(rows)
    if summary.status.eq("đã chạy").all():
        summary = summary.sort_values(["MAE_mean", "RMSE_mean", "config"]).reset_index(drop=True)
        summary.insert(0, "rank", np.arange(1, len(summary)+1))
        summary.to_csv(context["output"] / "feature_comparison.csv", index=False)
        summary.to_csv(context["root"] / "notebooks/features/feature_comparison.csv", index=False)
        export_selected(context, summary)
    return summary


def export_selected(context, summary):
    """Bàn giao feature chưa điền thiếu cùng ngữ cảnh, không fit model cuối."""
    winner = summary.iloc[0]["config"]
    output = context["root"] / "notebooks/features/selected" / context["protocol_id"]
    output.mkdir(parents=True, exist_ok=True)
    context["cohort"][["date_time", "traffic_volume", *CONFIGS[winner]]].to_csv(
        output / "train_features_unfitted.csv", index=False)
    context["train"].to_csv(output / "train_hourly_context.csv", index=False)
    write_json(output / "selection.json", dict(protocol_id=context["protocol_id"], config=winner,
               features=CONFIGS[winner], n=len(context["cohort"]), preprocessing_fitted=False,
               note="Tuning phải fit lại fill_weather theo từng fold, dùng train_hourly_context; không dùng median học toàn train.",
               selection_rule=context["metadata"]["selection"]))
    best = summary.iloc[0]
    lines = ["# Đối chứng đặc trưng bằng RF cố định", "",
             f"Protocol: `{context['protocol_id']}`. Chỉ dùng train; không chấm validation/test.", "",
             "| Phương án | Số cột | MAE CV ± SD (xe/giờ) | RMSE CV ± SD (xe/giờ) | n giờ chấm |",
             "|---|---:|---:|---:|---:|"]
    for row in summary.itertuples():
        lines.append(f"| {row.config} | {row.n_features} | {row.MAE_mean:.3f} ± {row.MAE_std:.3f} | {row.RMSE_mean:.3f} ± {row.RMSE_std:.3f} | {row.n} |")
    lines += ["", f"Chọn **{winner}** theo MAE trung bình fold thấp nhất ({best.MAE_mean:.3f} xe/giờ); RMSE dùng đối chiếu và phá hòa.",
              f"Cả năm dùng {len(context['cohort']):,}/{len(context['train']):,} giờ train có đủ lịch sử. n trong bảng là tổng các fold-score không trùng timestamp; mỗi phương án có 3 fold.",
              "SD mô tả biến động giữa các giai đoạn, không phải khoảng tin cậy của chênh lệch. Chưa kiểm định ý nghĩa thống kê và chưa ablation từng cột.",
              "Kết luận chỉ áp dụng cho RF/tham số/cohort này. Dự đoán tuần tự từng giờ được dùng target đã quan sát ở các giờ trước trong fold-score; chưa đại diện dự báo nhiều bước từ một mốc.",
              "Weather cùng giờ được giả định sẵn có. Nhãn lễ theo CSV có thể thiếu; timestamp chưa phân tích DST.",
              "", f"Dữ liệu bàn giao: `selected/{context['protocol_id']}/train_features_unfitted.csv`, kèm `train_hourly_context.csv` và `selection.json`. Chưa điền thiếu toàn train hoặc fit scaler/encoder; khi tuning phải dùng lại quy tắc xử lý trong `src/feature_experiments.py`."]
    text = "\n".join(lines) + "\n"
    (context["root"] / "notebooks/features/feature_summary.md").write_text(text, encoding="utf-8")
    (context["output"] / "feature_summary.md").write_text(text, encoding="utf-8")


def plot_scores(context, scores):
    """Hai đồ thị sai số theo fold, lưu PNG có protocol trong tên."""
    config = scores.config.iloc[0]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax, metric in zip(axes, ["MAE", "RMSE"]):
        ax.plot(scores.fold, scores[metric], marker="o", color="#207e8d")
        ax.set(xlabel="Fold theo thứ tự thời gian", ylabel=f"{metric} (xe/giờ)", xticks=[1, 2, 3],
               title=f"{metric} trung bình = {scores[metric].mean():.1f} xe/giờ")
        ax.grid(alpha=.25)
    fig.suptitle(f"{config}: sai số thay đổi theo giai đoạn đánh giá")
    fig.tight_layout()
    folder = context["root"] / "figures"
    folder.mkdir(exist_ok=True)
    fig.savefig(folder / f"feature_{config}_{context['protocol_id']}_cv.png", dpi=150, bbox_inches="tight")
    plt.show()
    plt.close(fig)
