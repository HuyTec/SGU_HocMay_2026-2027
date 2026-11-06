"""Các hàm chuẩn bị dữ liệu trước khi tạo đặc trưng."""

import pandas as pd

from .data_validation import validate_structure_and_time


def build_hourly_target(df: pd.DataFrame) -> pd.DataFrame:
    """Tạo bảng mục tiêu có một dòng cho mỗi giờ quan sát."""
    # Dừng nếu cấu trúc, timestamp hoặc mục tiêu theo giờ không hợp lệ.
    validate_structure_and_time(df)

    # Tạo bản sao và chuyển timestamp sang datetime.
    target_rows = df[["date_time", "traffic_volume"]].copy()
    target_rows["date_time"] = pd.to_datetime(
        target_rows["date_time"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",
    )

    # Validation đã xác nhận mỗi giờ có đúng một giá trị mục tiêu.
    return (
        target_rows.drop_duplicates()
        .sort_values("date_time")
        .reset_index(drop=True)
    )
def build_hourly_weather(df: pd.DataFrame) -> pd.DataFrame:
    """Tạo bảng thời tiết có một dòng cho mỗi giờ quan sát."""
    validate_structure_and_time(df)

    numeric_columns = ["temp", "rain_1h", "snow_1h", "clouds_all"]
    label_columns = ["weather_main", "weather_description"]

    # Tạo bản sao các cột cần dùng.
    weather_rows = df[numeric_columns + label_columns].copy()
    weather_rows["date_time"] = pd.to_datetime(
        df["date_time"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",
    )

    # Đánh dấu nhiệt độ 0 K là thiếu.
    weather_rows["temp"] = weather_rows["temp"].mask(
        weather_rows["temp"].eq(0)
    )

    # Tạm đánh dấu đúng điểm mưa nghi ngờ đã ghi trong validation.
    suspicious_rain = (
        weather_rows["date_time"].eq(pd.Timestamp("2016-07-11 17:00:00"))
        & weather_rows["rain_1h"].eq(9831.3)
    )
    weather_rows["rain_1h"] = weather_rows["rain_1h"].mask(
        suspicious_rain
    )

    # Thống nhất cách viết nhãn trước khi gộp.
    for column in label_columns:
        weather_rows[column] = (
            weather_rows[column].str.strip().str.lower()
        )

    # Mỗi số đo phân biệt được tính một lần trong cùng giờ.
    hourly_numeric = (
        weather_rows.groupby("date_time")[numeric_columns]
        .agg(lambda values: values.drop_duplicates().median())
    )

    # Giữ đủ nhãn duy nhất và sắp xếp để kết quả tái lập được.
    hourly_labels = (
        weather_rows.groupby("date_time")[label_columns]
        .agg(lambda labels: " | ".join(sorted(set(labels) - {""})))
    )

    return hourly_numeric.join(hourly_labels).reset_index()
def merge_hourly_data(
    hourly_target: pd.DataFrame,
    hourly_weather: pd.DataFrame,
) -> pd.DataFrame:
    """Ghép mục tiêu và thời tiết khi hai bảng khớp đầy đủ timestamp."""
    # Kiểm tra khóa ghép trước khi merge.
    for name, table in (
        ("hourly_target", hourly_target),
        ("hourly_weather", hourly_weather),
    ):
        if "date_time" not in table.columns:
            raise ValueError(f"{name} thiếu cột date_time.")

        if table["date_time"].isna().any():
            raise ValueError(f"{name} có timestamp bị thiếu.")

        if not table["date_time"].is_unique:
            raise ValueError(f"{name} có timestamp lặp.")

    # Các cột ngoài khóa phải riêng biệt để tránh xuất hiện hậu tố _x, _y.
    overlapping_columns = (
        set(hourly_target.columns) & set(hourly_weather.columns)
    ) - {"date_time"}

    if overlapping_columns:
        raise ValueError(
            f"Hai bảng có cột ngoài khóa bị trùng: {sorted(overlapping_columns)}"
        )

    merged = hourly_target.merge(
        hourly_weather,
        on="date_time",
        how="outer",
        validate="one_to_one",
        indicator=True,
        sort=True,
    )

    # Outer merge giúp phát hiện giờ chỉ xuất hiện ở một phía.
    unmatched = merged["_merge"].ne("both")
    if unmatched.any():
        examples = merged.loc[
            unmatched, ["date_time", "_merge"]
        ].head(5).to_dict("records")
        raise ValueError(f"Hai bảng chưa khớp timestamp. Ví dụ: {examples}")

    return merged.drop(columns="_merge")
def split_by_time(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Chia dữ liệu theo thời gian với tỷ lệ 70%, 15%, 15%."""
    if "date_time" not in df.columns:
        raise ValueError("Dữ liệu thiếu cột date_time.")

    if not pd.api.types.is_datetime64_any_dtype(df["date_time"]):
        raise ValueError("date_time phải có kiểu datetime.")

    if df["date_time"].isna().any():
        raise ValueError("Có timestamp bị thiếu.")

    if not df["date_time"].is_unique:
        raise ValueError("Có timestamp lặp, cần gộp theo giờ trước khi chia.")

    # Sắp xếp trên bảng mới để giữ nguyên dữ liệu đầu vào.
    ordered = df.sort_values("date_time").reset_index(drop=True)
    row_count = len(ordered)

    train_end = row_count * 70 // 100
    validation_end = row_count * 85 // 100

    if not 0 < train_end < validation_end < row_count:
        raise ValueError("Số dòng không đủ để tạo ba tập không rỗng.")

    return {
        "train": ordered.iloc[:train_end].copy(),
        "validation": ordered.iloc[train_end:validation_end].copy(),
        "test": ordered.iloc[validation_end:].copy(),
    }
def fit_weather_fill(train: pd.DataFrame) -> dict:
    """Học các thống kê điền thiếu chỉ từ train."""
    month = train["date_time"].dt.month.rename("month")
    hour = train["date_time"].dt.hour.rename("hour")

    temp_by_month_hour = (
        train.groupby([month, hour])["temp"].median().dropna()
    )
    temp_fallback = train["temp"].median()
    rain_median = train["rain_1h"].median()

    if pd.isna(temp_fallback) or pd.isna(rain_median):
        raise ValueError("Train thiếu giá trị hợp lệ để tính median.")

    return {
        "temp_by_month_hour": temp_by_month_hour,
        "temp_fallback": temp_fallback,
        "rain_median": rain_median,
    }


def fill_weather(
    data: pd.DataFrame,
    statistics: dict,
    history: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Điền thời tiết, chỉ tra nhiệt độ quan sát trước giờ thiếu."""
    result = data.copy()

    # Lịch sử phải lấy từ các bảng trước khi điền.
    observations = data[["date_time", "temp"]].copy()
    if history is not None:
        if not history.empty and not data.empty:
            if history["date_time"].max() >= data["date_time"].min():
                raise ValueError("Lịch sử phải nằm trước tập đang xử lý.")

        observations = pd.concat(
            [history[["date_time", "temp"]], observations],
            ignore_index=True,
        )

    if observations["date_time"].isna().any():
        raise ValueError("Có timestamp bị thiếu.")

    if not observations["date_time"].is_unique:
        raise ValueError("Có timestamp lặp trong dữ liệu tra nhiệt độ.")

    # Chỉ dùng nhiệt độ quan sát được, không dùng giá trị vừa điền.
    observations = (
        observations.loc[observations["temp"].notna()]
        .rename(columns={
            "date_time": "observed_time",
            "temp": "observed_temp",
        })
        .sort_values("observed_time")
    )

    missing_temp = result["temp"].isna()

    if missing_temp.any():
        missing_times = (
            result.loc[missing_temp, ["date_time"]]
            .sort_values("date_time")
        )

        # Tra đúng thời gian thực, giới hạn độ cũ tối đa 6 giờ.
        lookup = pd.merge_asof(
            missing_times,
            observations,
            left_on="date_time",
            right_on="observed_time",
            direction="backward",
            allow_exact_matches=False,
            tolerance=pd.Timedelta(hours=6),
        )

        # Tính giá trị dự phòng cho từng giờ thiếu.
        keys = pd.MultiIndex.from_arrays(
            [
                lookup["date_time"].dt.month,
                lookup["date_time"].dt.hour,
            ],
            names=["month", "hour"],
        )
        fallback = (
            statistics["temp_by_month_hour"]
            .reindex(keys)
            .fillna(statistics["temp_fallback"])
            .to_numpy()
        )

        lookup["filled_temp"] = lookup["observed_temp"].fillna(
            pd.Series(fallback, index=lookup.index)
        )
        filled_by_time = lookup.set_index("date_time")["filled_temp"]

        result.loc[missing_temp, "temp"] = (
            result.loc[missing_temp, "date_time"].map(filled_by_time)
        )

    result["rain_1h"] = result["rain_1h"].fillna(
        statistics["rain_median"]
    )

    return result
    