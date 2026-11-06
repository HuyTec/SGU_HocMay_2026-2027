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
