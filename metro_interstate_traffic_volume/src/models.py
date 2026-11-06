"""Cấu hình mô hình và tuning dùng chung để so sánh các phiên bản V_2–V_4.

Mọi cấu hình đầu vào dùng cùng lưới tham số, cùng số lượt thử và cùng fold theo
thời gian. Bước học tham số tiền xử lý nằm trong pipeline nên chỉ fit trên phần
train của từng fold.
"""

import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

from src.evaluation import clip_prediction, regression_metrics


RANDOM_STATE = 42
N_SPLITS = 3

# Ridge không tự tạo tương tác: thay các cột lịch bằng one-hot cặp thứ–giờ và tháng.
CALENDAR_FOR_RIDGE = {
    "hour", "day_of_week", "month", "is_weekend", "is_rush_hour",
    "hour_sin", "hour_cos", "day_of_week_sin", "day_of_week_cos",
    "month_sin", "month_cos",
}

SEARCH_SPACE = {
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
N_RANDOM_TRIALS = {"Random Forest": 6, "XGBoost": 12}


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
    if name == "XGBoost":
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


def tune_model(name: str, features: list[str], train: pd.DataFrame):
    """Chọn tham số theo MAE trên ba fold thời gian rồi fit lại trên toàn train."""
    settings = {
        "scoring": "neg_mean_absolute_error",
        "cv": TimeSeriesSplit(n_splits=N_SPLITS),
        "refit": True,
        "error_score": "raise",
        "n_jobs": 1,
    }
    estimator = make_model(name, features)
    if name == "Ridge":
        search = GridSearchCV(estimator, SEARCH_SPACE[name], **settings)
    else:
        search = RandomizedSearchCV(
            estimator,
            SEARCH_SPACE[name],
            n_iter=N_RANDOM_TRIALS[name],
            random_state=RANDOM_STATE,
            **settings,
        )
    return search.fit(train[input_columns(name, features)], train["traffic_volume"])


def summarize_search(search) -> pd.DataFrame:
    """Bảng tham số và MAE của từng fold, xếp theo thứ hạng."""
    rows = pd.DataFrame(search.cv_results_)
    table = pd.DataFrame({"parameters": rows["params"]})
    for fold in range(N_SPLITS):
        table[f"fold_{fold + 1}_mae"] = -rows[f"split{fold}_test_score"]
    table["mean_cv_mae"] = -rows["mean_test_score"]
    table["rank"] = rows["rank_test_score"]
    return table.sort_values("rank").reset_index(drop=True)


MODEL_NAMES = ["Ridge", "Random Forest", "XGBoost"]


def run_config(
    config: str,
    features: list[str],
    train: pd.DataFrame,
    target: pd.DataFrame,
    model_names: list[str] = MODEL_NAMES,
) -> list[dict]:
    """Tuning từng mô hình trên train rồi dự đoán các giờ trong target."""
    results = []
    for name in model_names:
        search = tune_model(name, features, train)
        prediction = search.predict(target[input_columns(name, features)])
        results.append(
            {
                "config": config,
                "model": name,
                "features": list(features),
                "search": search,
                "prediction": clip_prediction(prediction),
                "metrics": regression_metrics(target["traffic_volume"], prediction),
            }
        )
    return results


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
