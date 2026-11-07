"""Tuning theo thời gian, học xử lý thiếu trong từng fold của train."""

from dataclasses import dataclass

import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import ParameterGrid, ParameterSampler, TimeSeriesSplit

from src.evaluation import clip_prediction, regression_metrics
from src.models import (
    MODEL_NAMES, N_RANDOM_TRIALS, RANDOM_STATE, SEARCH_SPACE, input_columns, make_model,
)
from src.preprocessing import fill_weather, fit_weather_fill


N_SPLITS = 3


def _time_folds(train: pd.DataFrame):
    """Kiểm tra thứ tự trước khi chia fold mở rộng."""
    times = train["date_time"]
    if times.isna().any() or not times.is_unique or not times.is_monotonic_increasing:
        raise ValueError("Train phải có timestamp duy nhất và tăng dần.")
    for fit_idx, score_idx in TimeSeriesSplit(n_splits=N_SPLITS).split(train):
        yield train.iloc[fit_idx], train.iloc[score_idx]


def describe_folds(train: pd.DataFrame) -> pd.DataFrame:
    """Tạo bảng ranh giới và số giờ cho notebook."""
    return pd.DataFrame([
        {
            "fold": number,
            "fit_start": fit["date_time"].iloc[0],
            "fit_end": fit["date_time"].iloc[-1],
            "validation_start": score["date_time"].iloc[0],
            "validation_end": score["date_time"].iloc[-1],
            "n_fit": len(fit),
            "n_validation": len(score),
        }
        for number, (fit, score) in enumerate(_time_folds(train), start=1)
    ])


def _prepare_folds(train, features, raw_train):
    """Tạo đầu vào mỗi fold từ thời tiết gốc, giữ lịch sử quan sát theo thời gian."""
    weather_columns = set(features) & {"temp_c", "rain_1h"}
    if not weather_columns:
        return list(_time_folds(train))
    if raw_train is None:
        raise ValueError("Cấu hình thời tiết cần raw_train chưa điền để học median trong từng fold.")

    raw = raw_train[["date_time", "temp", "rain_1h"]].sort_values("date_time")
    times = raw["date_time"]
    if times.isna().any() or not times.is_unique or not train["date_time"].isin(times).all():
        raise ValueError("raw_train phải có một dòng cho mỗi giờ và bao phủ tập huấn luyện.")
    folds = []
    for fit, score in _time_folds(train):
        # Các giờ không đủ lag vẫn là quan sát thời tiết có sẵn.
        past = raw.loc[times.le(fit["date_time"].iloc[-1])]
        period = raw.loc[times.gt(past["date_time"].iloc[-1]) & times.le(score["date_time"].iloc[-1])]
        statistics = fit_weather_fill(past)
        fit_weather = fill_weather(past, statistics).set_index("date_time")
        score_weather = fill_weather(period, statistics, history=past).set_index("date_time")

        fit, score = fit.copy(), score.copy()
        for frame, weather in ((fit, fit_weather), (score, score_weather)):
            if "temp_c" in weather_columns:
                frame["temp_c"] = frame["date_time"].map(weather["temp"]) - 273.15
            if "rain_1h" in weather_columns:
                frame["rain_1h"] = frame["date_time"].map(weather["rain_1h"])
        folds.append((fit, score))
    return folds


@dataclass
class SearchResult:
    """Mô hình đã fit lại và bảng điểm CV cho các ứng viên."""

    best_estimator_: object
    best_params_: dict
    best_score_: float
    scores: pd.DataFrame

    def predict(self, inputs: pd.DataFrame):
        return self.best_estimator_.predict(inputs)


def _search(name, features, train, folds) -> SearchResult:
    columns = input_columns(name, features)
    space = SEARCH_SPACE[name]
    if name in N_RANDOM_TRIALS:
        candidates = ParameterSampler(space, N_RANDOM_TRIALS[name], random_state=RANDOM_STATE)
    else:
        candidates = ParameterGrid(space)
    rows = []
    for parameters in candidates:
        errors = {}
        for number, (fit, score) in enumerate(folds, start=1):
            model = make_model(name, features).set_params(**parameters)
            model.fit(fit[columns], fit["traffic_volume"])
            prediction = clip_prediction(model.predict(score[columns]))
            errors[f"fold_{number}_mae"] = mean_absolute_error(score["traffic_volume"], prediction)
        rows.append({
            "parameters": parameters, **errors,
            "mean_cv_mae": sum(errors.values()) / len(errors),
        })
    scores = pd.DataFrame(rows).sort_values("mean_cv_mae", kind="stable").reset_index(drop=True)
    scores["rank"] = scores["mean_cv_mae"].rank(method="min").astype(int)
    best = scores.iloc[0]
    model = make_model(name, features).set_params(**best["parameters"])
    model.fit(train[columns], train["traffic_volume"])
    return SearchResult(model, best["parameters"], -best["mean_cv_mae"], scores)


def tune_model(name, features, train, *, raw_train=None) -> SearchResult:
    """Chọn theo MAE CV và fit lại trên toàn bộ train đã chuẩn bị."""
    return _search(name, features, train, _prepare_folds(train, features, raw_train))


def summarize_search(search: SearchResult) -> pd.DataFrame:
    """Bảng tham số và MAE theo fold."""
    return search.scores.copy()


def run_config(config, features, train, target, model_names=MODEL_NAMES, *, raw_train=None):
    """Tuning trên train, rồi dự đoán tập validation ngoài bằng mô hình đã fit lại."""
    if target["date_time"].min() <= train["date_time"].max():
        raise ValueError("Tập đánh giá phải nằm sau train.")
    folds = _prepare_folds(train, features, raw_train)
    results = []
    for name in model_names:
        search = _search(name, features, train, folds)
        prediction = clip_prediction(search.predict(target[input_columns(name, features)]))
        results.append({
            "config": config,
            "model": name,
            "features": list(features),
            "search": search,
            "prediction": prediction,
            "metrics": regression_metrics(target["traffic_volume"], prediction),
        })
    return results
