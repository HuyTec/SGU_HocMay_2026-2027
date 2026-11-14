"""Grid CV theo thời gian cho Config B và pipeline dùng tham số chỉnh tay."""

import warnings

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import ParameterGrid, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src import features
from src.data import fill_missing_weather
from src.evaluation import clip_prediction, regression_metrics
from src.models import make_fixed_model


def make_config_b_pipeline(model_name, params):
    """Tạo pipeline cùng cách chuẩn hóa và estimator như thí nghiệm ngày 12."""
    steps = [("imputer", SimpleImputer(strategy="median"))]
    if model_name in ("Linear Regression", "MLP"):
        steps.append(("scaler", StandardScaler()))
    steps.append(("model", make_fixed_model(model_name, dict(params))))
    return Pipeline(steps)


def run_grid_cv(raw_train, model_params, param_grids, n_splits=3):
    """Đánh giá toàn bộ lưới, trả kết quả theo thứ tự khai báo để người dùng chọn."""
    if not raw_train["date_time"].is_monotonic_increasing:
        raise ValueError("Train phải được sắp xếp theo thời gian.")
    if raw_train["date_time"].duplicated().any():
        raise ValueError("Train có timestamp trùng.")

    # Chuẩn bị fold một lần, học thống kê điền thiếu từ phần train của fold.
    folds = []
    for train_idx, val_idx in TimeSeriesSplit(n_splits=n_splits).split(raw_train):
        parts = fill_missing_weather({
            "train": raw_train.iloc[train_idx].copy(),
            "validation": raw_train.iloc[val_idx].copy(),
        })
        prepared = {
            name: features.add_weather_features(features.add_time_features(frame))
            for name, frame in parts.items()
        }
        folds.append((prepared["train"], prepared["validation"]))

    rows = []
    for model_name, grid in param_grids.items():
        candidates = list(ParameterGrid(grid))
        for candidate_id, overrides in enumerate(candidates, start=1):
            params = {**model_params[model_name], **overrides}
            print(f"{model_name}: bộ {candidate_id}/{len(candidates)}", flush=True)
            row = {"model": model_name, "candidate_id": candidate_id, "params": params}
            scores = []
            messages = []
            for fold_id, (train, validation) in enumerate(folds, start=1):
                pipeline = make_config_b_pipeline(model_name, params)
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    pipeline.fit(train[features.CONFIG_B], train["traffic_volume"])
                    prediction = clip_prediction(pipeline.predict(validation[features.CONFIG_B]))
                if not np.isfinite(prediction).all():
                    raise ValueError(f"{model_name} có dự đoán không hữu hạn ở fold {fold_id}.")
                metrics = regression_metrics(validation["traffic_volume"], prediction)
                scores.append(metrics)
                row.update({f"fold_{fold_id}_{key}": value for key, value in metrics.items()})
                messages.extend(str(w.message) for w in caught)
            for metric in ("MAE", "RMSE", "R2"):
                values = [score[metric] for score in scores]
                row[f"mean_{metric}"] = float(np.mean(values))
                row[f"std_{metric}"] = float(np.std(values))
            row["warnings"] = " | ".join(dict.fromkeys(messages))
            rows.append(row)
    return pd.DataFrame(rows)
