"""Pipeline mô hình cho notebook báo cáo; mã lịch sử ở models_exp.py."""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import TransformedTargetRegressor
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from src.features import CONFIG_A, CONFIG_B, CONFIG_C, add_time_features, add_weather_features
from src.preprocessing import fill_weather, fit_weather_fill

RANDOM_STATE = 42
CONFIGS = {"A12": list(CONFIG_A), "B27": list(CONFIG_B), "C30": list(CONFIG_C)}
MODEL_NAMES = ("Ridge", "Random Forest", "Gradient Boosting", "MLP", "XGBoost")
SEARCH_SPACE = {
    "Ridge": {"model__alpha": [0.001, 0.01, 0.1, 1., 10., 100.]},
    "Random Forest": {"model__n_estimators": [100, 200, 400],
                      "model__max_depth": [8, 12, 16, 20, None],
                      "model__min_samples_leaf": [1, 2, 5, 10],
                      "model__max_features": [0.33, 0.5, 0.8, 1.0]},
    "Gradient Boosting": {"model__n_estimators": [100, 200], "model__learning_rate": [0.03, 0.1],
                          "model__max_depth": [2, 3]},
    "MLP": {"model__regressor__hidden_layer_sizes": [(32,), (64,), (64, 32)],
            "model__regressor__alpha": [0.0001, 0.01],
            "model__regressor__learning_rate_init": [0.001, 0.003]},
    "XGBoost": {"model__learning_rate": [0.03, 0.1], "model__max_depth": [4, 6],
                "model__min_child_weight": [1, 5], "model__subsample": [0.8, 1.0]},
}


class HourlyFeatures(TransformerMixin, BaseEstimator):
    """Fit median trên đúng fold-train, tạo feature và chỉ chọn cột cấu hình.

    weather_context chỉ chứa timestamp/nhiệt độ gốc, kể cả giờ ngoài cohort.
    Tra theo hướng backward nên từng giờ chỉ nhận quan sát trước nó; dữ liệu
    tại các timestamp của X luôn thay thế ngữ cảnh, không lấy lại ô đã che.
    History phải được tạo theo timestamp trước khi lọc cohort/chia fold.
    """
    def __init__(self, features, weather_context=None):
        self.features = features
        self.weather_context = weather_context

    def fit(self, X, y=None):
        self.statistics_ = fit_weather_fill(X)
        self.observations_ = X[["date_time", "temp"]].copy()
        self.n_fit_ = len(X)
        return self

    def transform(self, X):
        if not hasattr(self, "statistics_"):
            raise ValueError("Cần fit pipeline trên fold-train trước transform.")
        if X.empty:
            raise ValueError("Không transform bảng rỗng.")
        sources = [self.observations_]
        if self.weather_context is not None:
            sources.insert(0, self.weather_context[["date_time", "temp"]])
        sources.append(X[["date_time", "temp"]])
        observed = pd.concat(sources, ignore_index=True).drop_duplicates("date_time", keep="last")
        observed = observed.loc[observed.date_time.le(X.date_time.max())].sort_values("date_time")
        temperatures = fill_weather(observed.assign(rain_1h=0.), self.statistics_).set_index("date_time").temp
        prepared = X.copy()
        prepared["temp"] = prepared.date_time.map(temperatures)
        prepared["rain_1h"] = prepared.rain_1h.fillna(self.statistics_["rain_median"])
        featured = add_weather_features(add_time_features(prepared))
        matrix = featured[list(self.features)].to_numpy(dtype="float32")
        if not np.isfinite(matrix).all():
            raise ValueError("Feature còn NaN/inf; kiểm tra cohort/history, không tự bỏ dòng.")
        return np.ascontiguousarray(matrix)


def make_model(name, features, *, weather_context=None, random_state=RANDOM_STATE):
    """Tạo pipeline chưa fit; cùng cột A12/B27/C30, không thay biểu diễn lịch."""
    if name not in MODEL_NAMES:
        raise ValueError(f"Mô hình báo cáo không hỗ trợ: {name}")
    estimators = {
        "Ridge": lambda: Ridge(),
        "Random Forest": lambda: RandomForestRegressor(n_estimators=400, random_state=random_state, n_jobs=4),
        "Gradient Boosting": lambda: GradientBoostingRegressor(random_state=random_state),
        "MLP": lambda: TransformedTargetRegressor(
            regressor=MLPRegressor(max_iter=500, random_state=random_state), transformer=StandardScaler()),
        "XGBoost": lambda: _xgboost(random_state),
    }
    steps = [("features", HourlyFeatures(features, weather_context))]
    if name in ("Ridge", "MLP"):
        steps.append(("scaler", StandardScaler()))
    steps.append(("model", estimators[name]()))
    return Pipeline(steps)


def _xgboost(random_state):
    from xgboost import XGBRegressor
    return XGBRegressor(n_estimators=400, objective="reg:squarederror", tree_method="hist",
                        n_jobs=4, random_state=random_state)


class FeatureColumns(TransformerMixin, BaseEstimator):
    """Chọn cột từ ma trận FE đã điền thiếu, giữ layout float32 như RF của FE."""
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        values = np.ascontiguousarray(X[list(self.columns)], dtype="float32")
        if not np.isfinite(values).all():
            raise ValueError("Ma trận FE còn NaN/inf; không tự điền median cho lag.")
        return values


def make_cv_model(name, features):
    """Pipeline tuning nhận ma trận từ prepare_fold; không điền thiếu lần hai.

    Ridge thay biểu diễn lịch bằng one-hot weekday_hour/month. Các cột số
    còn lại được chuẩn hóa riêng trên fold-train. weekday_hour là cột dẫn
    xuất, không phải nguồn thông tin mới ngoài danh sách feature đã chốt.
    """
    model = make_model(name, features).named_steps["model"]
    if name == "Ridge":
        calendar = {"hour", "day_of_week", "month", "is_weekend", "is_rush_hour",
                    "hour_sin", "hour_cos", "day_of_week_sin", "day_of_week_cos", "month_sin", "month_cos"}
        numeric = [f for f in features if f not in calendar]
        columns = ColumnTransformer([
            ("calendar", OneHotEncoder(handle_unknown="ignore"), ["weekday_hour", "month"]),
            ("numeric", StandardScaler(), numeric),
        ])
    else:
        columns = FeatureColumns(tuple(features))
    steps = [("columns", columns)]
    if name == "MLP":
        steps.append(("scaler", StandardScaler()))
    return Pipeline([*steps, ("model", model)])
