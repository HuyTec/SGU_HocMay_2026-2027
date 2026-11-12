"""Tạo mô hình hồi quy, khai báo phạm vi tham số và đọc/ghi kết quả."""


import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
DEMO_MODEL_NAMES = ["Linear Regression", "Random Forest", "Gradient Boosting", "MLP"]
MODEL_NAMES = [*DEMO_MODEL_NAMES, "Ridge", "XGBoost"]

# Ridge không tự tạo tương tác: thay các cột lịch bằng one-hot cặp thứ–giờ và tháng.
CALENDAR_FOR_RIDGE = {
    "hour", "day_of_week", "month", "is_weekend", "is_rush_hour",
    "hour_sin", "hour_cos", "day_of_week_sin", "day_of_week_cos",
    "month_sin", "month_cos",
}

SEARCH_SPACE = {
    "Linear Regression": {},
    "Gradient Boosting": {
        "model__n_estimators": [100, 200],
        "model__learning_rate": [0.03, 0.1],
        "model__max_depth": [2, 3],
    },
    "MLP": {
        "model__hidden_layer_sizes": [(32,), (64,), (64, 32)],
        "model__alpha": [0.0001, 0.01],
        "model__learning_rate_init": [0.001, 0.003],
    },
    "Ridge": {"model__alpha": [0.1, 1.0, 10.0, 100.0, 1000.0]},
    "Random Forest": {
        "max_depth": [12, 16, 20, None],
        "min_samples_leaf": [1, 2, 5, 10],
        "max_features": [0.33, 0.5, 0.8],
    },
    "XGBoost": {
        "learning_rate": [0.03, 0.05, 0.1],
        "max_depth": [4, 5, 6, 8],
        "min_child_weight": [1, 5, 10],
        "subsample": [0.7, 0.85, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
    },
}
N_RANDOM_TRIALS = {"Random Forest": 6, "XGBoost": 12, "Gradient Boosting": 6, "MLP": 6}
FIXED_MODEL_CLASSES = {
    "Linear Regression": LinearRegression,
    "Random Forest": RandomForestRegressor,
    "Gradient Boosting": GradientBoostingRegressor,
    "MLP": MLPRegressor,
}


def make_fixed_model(name: str, params: dict):
    """Khởi tạo một mô hình từ tham số trong notebook."""
    if name not in FIXED_MODEL_CLASSES:
        raise ValueError(f"Mô hình không được hỗ trợ: {name}")

    model = FIXED_MODEL_CLASSES[name](**params)

    if name == "MLP":
        return TransformedTargetRegressor(
            regressor=model,
            transformer=StandardScaler(),
        )

    return model

def ridge_one_hot(features: list[str]) -> list[str]:
    """Cột one-hot của Ridge, chỉ gồm thông tin có trong cấu hình đang xét."""
    columns = ["weekday_hour"]
    if "month" in features:
        columns.append("month")
    return columns


def ridge_numeric(features: list[str]) -> list[str]:
    """Các cột còn lại của Ridge, được điền thiếu và chuẩn hóa trong fold."""
    return [col for col in features if col not in CALENDAR_FOR_RIDGE]


def ridge_columns(features: list[str]) -> list[str]:
    """Toàn bộ cột đầu vào của Ridge."""
    return ridge_one_hot(features) + ridge_numeric(features)


def make_ridge(features: list[str]) -> Pipeline:
    """Ridge có tương tác thứ–giờ; bước fit tiền xử lý nằm trong pipeline."""
    transformers = [
        ("calendar", OneHotEncoder(handle_unknown="ignore"), ridge_one_hot(features))
    ]
    numeric = ridge_numeric(features)
    if numeric:
        transformers.append(
            (
                "numeric",
                make_pipeline(
                    SimpleImputer(strategy="median", add_indicator=True),
                    StandardScaler(),
                ),
                numeric,
            )
        )
    return Pipeline(
        [("preprocessor", ColumnTransformer(transformers)), ("model", Ridge())]
    )


def make_model(name: str, features: list[str]):
    """Tạo mô hình chưa fit theo tên."""
    if name == "Ridge":
        return make_ridge(features)
    if name == "Random Forest":
        return make_forest()
    if name == "Linear Regression":
        return make_pipeline(SimpleImputer(strategy="median"), LinearRegression())
    if name == "Gradient Boosting":
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", GradientBoostingRegressor(random_state=RANDOM_STATE)),
        ])
    if name == "MLP":
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", MLPRegressor(random_state=RANDOM_STATE, max_iter=500)),
        ])
    if name == "XGBoost":
        from xgboost import XGBRegressor

        return XGBRegressor(
            n_estimators=400,
            objective="reg:squarederror",
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    raise ValueError(f"Không có mô hình {name}.")


def make_forest() -> RandomForestRegressor:
    """Random Forest của scikit-learn nhận được NaN nên không cần imputer."""
    return RandomForestRegressor(
        n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1
    )


def input_columns(name: str, features: list[str]) -> list[str]:
    """Danh sách cột cần đưa vào mô hình."""
    return ridge_columns(features) if name == "Ridge" else list(features)


def results_table(results: list[dict]) -> pd.DataFrame:
    """Bảng metrics và MAE CV của các kết quả từ run_config."""
    rows = []
    for item in results:
        rows.append(
            {
                "config": item["config"],
                "model": item["model"],
                "so_dac_trung": len(item["features"]),
                **item["metrics"],
                "mean_cv_mae": -item["search"].best_score_,
            }
        )
    return pd.DataFrame(rows)


def save_results(
    version: str,
    results: list[dict],
    target: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Lưu metrics, tham số được chọn và dự đoán validation để notebook sau dùng lại."""
    metric_dir = output_dir / "metrics"
    prediction_dir = output_dir / "predictions"
    metric_dir.mkdir(parents=True, exist_ok=True)
    prediction_dir.mkdir(parents=True, exist_ok=True)

    results_table(results).to_csv(metric_dir / f"{version}_validation.csv", index=False)
    parameters = {
        f"{item['config']}|{item['model']}": item["search"].best_params_
        for item in results
    }
    (metric_dir / f"{version}_best_params.json").write_text(
        json.dumps(parameters, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    predictions = target[["date_time", "traffic_volume"]].copy()
    for item in results:
        predictions[f"{item['config']}|{item['model']}"] = item["prediction"].round(3)
    predictions.to_csv(prediction_dir / f"{version}_validation.csv", index=False)


def load_predictions(version: str, output_dir: Path) -> pd.DataFrame:
    """Đọc dự đoán đã lưu; báo rõ notebook cần chạy trước nếu chưa có file."""
    path = output_dir / "predictions" / f"{version}_validation.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Chưa có {path}; hãy chạy notebook {version} trước.")
    return pd.read_csv(path, parse_dates=["date_time"])


def load_best_params(version: str, output_dir: Path) -> dict:
    """Đọc tham số được chọn của một phiên bản."""
    path = output_dir / "metrics" / f"{version}_best_params.json"
    if not path.is_file():
        raise FileNotFoundError(f"Chưa có {path}; hãy chạy notebook {version} trước.")
    return json.loads(path.read_text(encoding="utf-8"))
