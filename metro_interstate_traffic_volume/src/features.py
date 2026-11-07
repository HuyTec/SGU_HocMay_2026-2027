"""Các hàm tạo đặc trưng cho dữ liệu giao thông."""

import pandas as pd


def add_holiday_features(
    hourly_data: pd.DataFrame,
    raw_data: pd.DataFrame,
) -> pd.DataFrame:
    """Gắn tên và cờ sự kiện cho các giờ quan sát trong cùng ngày."""
    required_raw = {"date_time", "holiday"}
    missing_columns = required_raw - set(raw_data.columns)
    if missing_columns:
        raise ValueError(f"CSV gốc thiếu cột: {sorted(missing_columns)}")

    if "date_time" not in hourly_data.columns:
        raise ValueError("Bảng theo giờ thiếu date_time.")

    if raw_data[["date_time", "holiday"]].isna().any().any():
        raise ValueError("CSV gốc có ngày giờ hoặc nhãn sự kiện bị thiếu.")

    # Tạo khóa ngày từ timestamp của CSV gốc.
    raw_dates = pd.to_datetime(
        raw_data["date_time"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",
    ).dt.normalize()
    holiday_labels = raw_data["holiday"].astype("string").str.strip()

    if holiday_labels.eq("").any():
        raise ValueError("CSV gốc có nhãn sự kiện là chuỗi rỗng.")

    # Chuỗi 'None' biểu thị ngày không được ghi nhận nhãn sự kiện.
    has_event = holiday_labels.ne("None")
    events = (
        pd.DataFrame({
            "date": raw_dates,
            "holiday_name": holiday_labels,
        })
        .loc[has_event]
        .drop_duplicates()
    )

    # Dừng nếu một ngày có nhiều tên sự kiện khác nhau.
    if events["date"].duplicated().any():
        raise ValueError("Có ngày mang nhiều tên sự kiện.")

    name_by_date = events.set_index("date")["holiday_name"]

    # Gắn nhãn vào bản sao, giữ thứ tự dòng của bảng đầu vào.
    result = hourly_data.copy()
    observed_dates = pd.to_datetime(
        result["date_time"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",
    ).dt.normalize()

    if observed_dates.isna().any():
        raise ValueError("Bảng theo giờ có timestamp bị thiếu.")

    event_names = observed_dates.map(name_by_date)

    # Dùng object để khớp kiểu dữ liệu của phần thử nghiệm notebook.
    result["holiday_name"] = event_names.fillna("None").astype(object)
    result["is_holiday"] = event_names.notna().astype("int8")

    return result
def add_time_temperature_features(df: pd.DataFrame) -> pd.DataFrame:
    """Tạo đặc trưng thời gian và đổi nhiệt độ Kelvin sang Celsius."""
    required_columns = {"date_time", "temp"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Dữ liệu thiếu cột: {sorted(missing_columns)}")

    if not pd.api.types.is_datetime64_any_dtype(df["date_time"]):
        raise ValueError("date_time phải có kiểu datetime.")

    if df[["date_time", "temp"]].isna().any().any():
        raise ValueError("Cần xử lý timestamp hoặc nhiệt độ thiếu trước.")

    if not pd.api.types.is_numeric_dtype(df["temp"]):
        raise ValueError("temp phải có kiểu số và đơn vị Kelvin.")

    result = df.copy()
    timestamps = result["date_time"]

    # Thứ Hai = 0, ..., Chủ nhật = 6.
    result["hour"] = timestamps.dt.hour.astype("int8")
    result["day_of_week"] = timestamps.dt.dayofweek.astype("int8")
    result["month"] = timestamps.dt.month.astype("int8")
    result["is_weekend"] = result["day_of_week"].ge(5).astype("int8")

    # Tạm giữ temp để đối chiếu, chọn cột bàn giao ở bước chốt dữ liệu.
    result["temp_c"] = result["temp"] - 273.15

    return result
CATEGORY_PREFIXES = {
    "weather_main": "weather_main",
    "weather_description": "weather_description",
    "holiday_name": "holiday",
}


def _parse_category_labels(df: pd.DataFrame) -> dict:
    """Chuẩn hóa từng ô phân loại thành một tập nhãn."""
    missing_columns = set(CATEGORY_PREFIXES) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Dữ liệu thiếu cột: {sorted(missing_columns)}")

    if df[list(CATEGORY_PREFIXES)].isna().any().any():
        raise ValueError("Có ô phân loại bị thiếu thực sự.")

    parsed = {}

    for column in CATEGORY_PREFIXES:
        values = df[column].astype("string").str.strip()

        if column == "holiday_name":
            # Giữ tên sự kiện và xem chuỗi 'None' là không có nhãn.
            if values.eq("").any():
                raise ValueError("holiday_name có chuỗi rỗng.")

            labels = values.map(
                lambda value: set() if value == "None" else {value}
            )
        else:
            # Loại khoảng trắng, thống nhất chữ thường và bỏ nhãn trùng.
            labels = values.map(
                lambda value: {
                    label.strip().lower()
                    for label in value.split("|")
                    if label.strip()
                }
            )

            if labels.map(len).eq(0).any():
                raise ValueError(f"{column} có giờ không có nhãn.")

        parsed[column] = labels

    return parsed


def fit_category_vocabulary(train: pd.DataFrame) -> dict:
    """Học danh sách nhãn phân loại từ train."""
    if train.empty:
        raise ValueError("Train không có dòng để học danh sách nhãn.")

    parsed = _parse_category_labels(train)

    return {
        column: sorted(set().union(*parsed[column]))
        for column in CATEGORY_PREFIXES
    }


def encode_categories(
    df: pd.DataFrame,
    vocabularies: dict,
) -> pd.DataFrame:
    """Mã hóa bằng danh sách nhãn đã học, giữ cờ nhãn mới."""
    parsed = _parse_category_labels(df)
    result = df.drop(columns=list(CATEGORY_PREFIXES)).copy()

    for column, prefix in CATEGORY_PREFIXES.items():
        labels = parsed[column]
        vocabulary = vocabularies[column]
        known_labels = set(vocabulary)

        # Tạo từng cột theo đúng thứ tự danh sách nhãn đã học.
        for label in vocabulary:
            result[f"{prefix}_{label}"] = labels.map(
                lambda values: int(label in values)
            ).astype("int8")

        # Giữ nhãn đã biết và ghi nhận nếu cùng giờ còn nhãn mới.
        result[f"{prefix}_unknown"] = labels.map(
            lambda values: int(bool(values - known_labels))
        ).astype("int8")

    return result
def select_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Chọn Celsius làm cột nhiệt độ cho dữ liệu bàn giao."""
    required_columns = {"temp", "temp_c"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Dữ liệu thiếu cột: {sorted(missing_columns)}")

    return df.drop(columns="temp").copy()




import numpy as np


# Giờ cao điểm ngày làm việc; căn cứ từ bảng trung bình theo giờ của train
# trong notebooks/experiments/V_2.ipynb.
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
