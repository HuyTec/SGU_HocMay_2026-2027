"""Metrics, hai baseline thống kê và bảng sai số theo nhóm."""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def clip_prediction(prediction) -> np.ndarray:
    """Lưu lượng không âm nên cắt dự đoán âm về 0 trước khi đánh giá."""
    return np.clip(np.asarray(prediction, dtype="float64"), 0, None)


def regression_metrics(y_true, prediction) -> dict[str, float]:
    """Tính MAE, RMSE (xe/giờ) và R² trên cùng tập đánh giá."""
    prediction = clip_prediction(prediction)
    return {
        "MAE": float(mean_absolute_error(y_true, prediction)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, prediction))),
        "R2": float(r2_score(y_true, prediction)),
    }


def weekday_hour_baseline(train: pd.DataFrame, target: pd.DataFrame) -> np.ndarray:
    """Trung bình theo cặp thứ–giờ của train; thiếu nhóm thì dùng trung bình train."""
    means = train.groupby(["day_of_week", "hour"])["traffic_volume"].mean()
    keys = pd.MultiIndex.from_frame(target[["day_of_week", "hour"]])
    return (
        means.reindex(keys).fillna(train["traffic_volume"].mean()).to_numpy()
    )


def seasonal_naive(target: pd.DataFrame) -> np.ndarray:
    """Dự đoán bằng lưu lượng quan sát tại t − 7 ngày; thiếu lịch sử trả NaN."""
    return target["lag_168h"].to_numpy(dtype="float64")


def errors_by_group(
    frame: pd.DataFrame, group, prediction, name: str = "nhom"
) -> pd.DataFrame:
    """Bảng số mẫu, MAE và sai số trung bình theo nhóm; sai số = dự đoán − thực tế."""
    errors = pd.DataFrame(
        {
            name: group,
            "actual": frame["traffic_volume"].to_numpy(),
            "error": clip_prediction(prediction) - frame["traffic_volume"].to_numpy(),
        }
    )
    errors["absolute"] = errors["error"].abs()
    return errors.groupby(name, observed=True).agg(
        so_gio=("error", "size"),
        luu_luong_tb=("actual", "mean"),
        MAE=("absolute", "mean"),
        sai_so_tb=("error", "mean"),
    )


def bootstrap_mae_difference(
    frame: pd.DataFrame,
    prediction_a,
    prediction_b,
    n_boot: int = 2000,
    seed: int = 42,
) -> dict[str, float]:
    """Khoảng tin cậy 95% của MAE(A) − MAE(B), lấy mẫu lại theo từng ngày.

    Các giờ trong cùng ngày tương quan với nhau nên không lấy mẫu theo từng giờ.
    Giá trị dương nghĩa là B có MAE thấp hơn A trên tập đang xét.
    """
    actual = frame["traffic_volume"].to_numpy()
    gain = (
        np.abs(clip_prediction(prediction_a) - actual)
        - np.abs(clip_prediction(prediction_b) - actual)
    )
    by_day = (
        pd.DataFrame({"day": frame["date_time"].dt.normalize().to_numpy(), "gain": gain})
        .groupby("day")["gain"]
        .agg(["sum", "size"])
    )
    rng = np.random.default_rng(seed)
    picks = rng.integers(0, len(by_day), size=(n_boot, len(by_day)))
    totals = by_day["sum"].to_numpy()[picks].sum(axis=1)
    counts = by_day["size"].to_numpy()[picks].sum(axis=1)
    samples = totals / counts
    return {
        "chenh_lech_MAE": float(gain.mean()),
        "CI95_thap": float(np.quantile(samples, 0.025)),
        "CI95_cao": float(np.quantile(samples, 0.975)),
        "so_ngay": int(len(by_day)),
    }


def run_observations(data_path, splits: dict[str, pd.DataFrame], notebook: str) -> list[str]:
    """Thông tin chung của một lần chạy để ghi vào nhật ký thực nghiệm."""
    import hashlib
    import platform
    import subprocess

    import sklearn
    import xgboost

    def git_output(*args: str) -> str:
        done = subprocess.run(
            ["git", *args], capture_output=True, text=True, cwd=str(data_path.parent)
        )
        return done.stdout.strip() if done.returncode == 0 else "không xác định"

    train, validation, test = (splits[n] for n in ("train", "validation", "test"))
    return [
        f"CSV SHA-256: {hashlib.sha256(data_path.read_bytes()).hexdigest()}",
        f"Train: {len(train)} giờ; {train.date_time.min()} đến {train.date_time.max()}.",
        f"Validation: {len(validation)} giờ; "
        f"{validation.date_time.min()} đến {validation.date_time.max()}.",
        f"Test: {len(test)} giờ; giữ riêng, chưa đánh giá.",
        f"Python {platform.python_version()}; pandas {pd.__version__}; "
        f"scikit-learn {sklearn.__version__}; xgboost {xgboost.__version__}.",
        f"Notebook: {notebook}; commit gốc {git_output('rev-parse', '--short', 'HEAD')}"
        + ("; có thay đổi chưa commit." if git_output("status", "--porcelain") else "."),
    ]
