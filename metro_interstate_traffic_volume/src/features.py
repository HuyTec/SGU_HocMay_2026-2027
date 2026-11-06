"""Tạo đặc trưng thời gian, thời tiết và lịch sử; các hàm không học tham số.

Đặc trưng lịch sử tra theo timestamp thực vì dữ liệu còn thiếu giờ: không dùng
shift theo số dòng và không dùng lưu lượng của chính giờ đang dự đoán.
"""

import numpy as np
import pandas as pd


# Giờ cao điểm ngày làm việc; căn cứ từ bảng trung bình theo giờ của train
# trong notebooks/BASELINE/baseline_V_2.ipynb.
RUSH_HOURS = (6, 7, 8, 15, 16, 17)

# 11 nhãn weather_main sau khi chuẩn hóa chữ thường, đều xuất hiện trong train.
WEATHER_GROUPS = (
    "clear", "clouds", "drizzle", "fog", "haze", "mist",
    "rain", "smoke", "snow", "squall", "thunderstorm",
)

# Số giờ quan sát tối thiểu trong 24 giờ trước để tính mean_24h.
MIN_HOURS_FOR_MEAN = 18

V1_FEATURES = ["hour", "day_of_week"]
CALENDAR_FEATURES = [
    "hour", "day_of_week", "month", "is_weekend", "is_rush_hour",
    "hour_sin", "hour_cos", "day_of_week_sin", "day_of_week_cos",
    "month_sin", "month_cos",
]
TIME_FEATURES = CALENDAR_FEATURES + ["is_holiday"]
WEATHER_NUMERIC_FEATURES = ["temp_c", "rain_1h", "snow_1h", "clouds_all"]
WEATHER_GROUP_FEATURES = [f"weather_{name}" for name in WEATHER_GROUPS]
WEATHER_FEATURES = WEATHER_NUMERIC_FEATURES + WEATHER_GROUP_FEATURES
HISTORY_FEATURES = ["lag_24h", "lag_168h", "mean_24h"]

CONFIG_A = TIME_FEATURES
CONFIG_B = TIME_FEATURES + WEATHER_FEATURES
CONFIG_C = TIME_FEATURES + WEATHER_FEATURES + HISTORY_FEATURES


def add_time_features(table: pd.DataFrame) -> pd.DataFrame:
    """Thêm đặc trưng lịch, mã hóa tuần hoàn và đổi nhiệt độ sang °C."""
    result = table.copy()
    times = result["date_time"]
    result["hour"] = times.dt.hour.astype("int8")
    result["day_of_week"] = times.dt.dayofweek.astype("int8")
    result["month"] = times.dt.month.astype("int8")
    result["is_weekend"] = result["day_of_week"].ge(5).astype("int8")
    result["is_rush_hour"] = (
        result["hour"].isin(RUSH_HOURS) & result["is_weekend"].eq(0)
    ).astype("int8")
    for col, period, offset in [
        ("hour", 24, 0), ("day_of_week", 7, 0), ("month", 12, 1)
    ]:
        angle = 2 * np.pi * (result[col] - offset) / period
        result[f"{col}_sin"] = np.sin(angle)
        result[f"{col}_cos"] = np.cos(angle)
    # Cặp thứ–giờ cho mô hình tuyến tính vì Ridge không tự tạo tương tác.
    result["weekday_hour"] = (
        result["day_of_week"].astype("int16") * 24 + result["hour"]
    )
    return result


def add_weather_features(table: pd.DataFrame) -> pd.DataFrame:
    """Đổi °C và tách nhãn gộp thành cờ 0/1 theo từng nhóm thời tiết.

    Một giờ có thể mang nhiều nhãn như "drizzle | rain"; one-hot trực tiếp trên
    chuỗi gộp sẽ tạo các tổ hợp hiếm và có tổ hợp không xuất hiện trong train.
    """
    result = table.copy()
    result["temp_c"] = result["temp"] - 273.15
    groups = result["weather_main"].str.split(" | ", regex=False)
    for name in WEATHER_GROUPS:
        result[f"weather_{name}"] = groups.map(lambda labels: name in labels).astype("int8")
    known = groups.map(lambda labels: set(labels) <= set(WEATHER_GROUPS))
    if not known.all():
        unknown = sorted(set(groups[~known].explode()) - set(WEATHER_GROUPS))
        raise ValueError(f"Có nhãn weather_main ngoài danh sách: {unknown}")
    return result


def add_history_features(table: pd.DataFrame) -> pd.DataFrame:
    """Thêm lag_24h, lag_168h và mean_24h, tra theo timestamp thực.

    Giờ không có lịch sử giữ NaN. table cần chứa toàn bộ các giờ đã quan sát
    trước giờ dự đoán, vì vậy gọi hàm trước khi lọc từng tập.
    """
    result = table.copy()
    times = result["date_time"]
    volume = result.set_index("date_time")["traffic_volume"].sort_index()
    for hours, col in [(24, "lag_24h"), (168, "lag_168h")]:
        result[col] = (times - pd.Timedelta(hours=hours)).map(volume).astype("float64")
    # closed="left" loại chính giờ đang dự đoán khỏi cửa sổ.
    rolling = volume.astype("float64").rolling(
        "24h", closed="left", min_periods=MIN_HOURS_FOR_MEAN
    ).mean()
    result["mean_24h"] = times.map(rolling)
    return result


def build_features(splits: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Tạo đầy đủ đặc trưng cho ba tập và giữ nguyên ranh giới giữa các tập."""
    combined = pd.concat(
        [part.assign(split=name) for name, part in splits.items()],
        ignore_index=True,
    ).sort_values("date_time")
    featured = add_history_features(add_weather_features(add_time_features(combined)))
    return {
        name: featured.loc[featured["split"].eq(name)]
        .drop(columns="split")
        .reset_index(drop=True)
        for name in splits
    }


def has_history(table: pd.DataFrame) -> pd.Series:
    """Đánh dấu các giờ có đủ ba đặc trưng lịch sử."""
    return table[HISTORY_FEATURES].notna().all(axis=1)
