"""Đọc CSV gốc và tạo bảng một dòng mỗi giờ.

Quy tắc mặc định giống notebooks/preprocessing/preprocessing_features.ipynb (Bước 02–07).
Các tham số mask_stuck_temp và complete_holidays mặc định tắt: đây là các
phương án đề xuất thêm, chỉ bật khi nhóm đã thống nhất hoặc khi kiểm tra độ nhạy.
"""

from pathlib import Path

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

from src.preprocessing import fill_weather, fit_weather_fill, split_by_time


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "Metro_Interstate_Traffic_Volume.csv"

WEATHER_NUMERIC = ["temp", "rain_1h", "snow_1h", "clouds_all"]
WEATHER_LABELS = ["weather_main", "weather_description"]

# Giá trị lặp bất thường đã ghi nhận trong notebooks/eda/data_validation.ipynb.
STUCK_TEMP_K = 276.793
RAIN_OUTLIER_TIME = pd.Timestamp("2016-07-11 17:00:00")
RAIN_OUTLIER_VALUE = 9831.3


def load_raw(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Đọc CSV, giữ chuỗi "None" của cột holiday và parse date_time."""
    raw = pd.read_csv(path, keep_default_na=False)
    raw["date_time"] = pd.to_datetime(
        raw["date_time"], format="%Y-%m-%d %H:%M:%S", errors="raise"
    )
    times = raw["date_time"]
    if not times.eq(times.dt.floor("h")).all():
        raise ValueError("Có timestamp không nằm đúng đầu giờ.")
    return raw


def build_hourly_target(raw: pd.DataFrame) -> pd.DataFrame:
    """Giữ một giá trị lưu lượng cho mỗi giờ; dừng nếu các dòng mâu thuẫn."""
    targets = raw[["date_time", "traffic_volume"]]
    counts = targets.groupby("date_time")["traffic_volume"].nunique()
    if counts.ne(1).any():
        raise ValueError("Có giờ mang nhiều giá trị traffic_volume khác nhau.")
    return (
        targets.drop_duplicates()
        .sort_values("date_time")
        .reset_index(drop=True)
    )


def build_hourly_weather(
    raw: pd.DataFrame, mask_stuck_temp: bool = False
) -> pd.DataFrame:
    """Gộp thời tiết theo giờ: median trên giá trị phân biệt, nhãn dạng tập hợp."""
    rows = raw[["date_time"] + WEATHER_NUMERIC + WEATHER_LABELS].copy()
    rows["temp"] = rows["temp"].mask(rows["temp"].eq(0))
    if mask_stuck_temp:
        rows["temp"] = rows["temp"].mask(rows["temp"].eq(STUCK_TEMP_K))
    rows["rain_1h"] = rows["rain_1h"].mask(
        rows["date_time"].eq(RAIN_OUTLIER_TIME)
        & rows["rain_1h"].eq(RAIN_OUTLIER_VALUE)
    )
    for col in WEATHER_LABELS:
        rows[col] = rows[col].str.strip().str.lower()

    # Một số đo lặp ở nhiều dòng nhãn chỉ được tính một lần trong median.
    numeric = pd.concat(
        [
            rows[["date_time", col]]
            .drop_duplicates()
            .groupby("date_time")[col]
            .median()
            for col in WEATHER_NUMERIC
        ],
        axis=1,
    )
    labels = rows.groupby("date_time")[WEATHER_LABELS].agg(
        lambda values: " | ".join(sorted(set(values) - {""}))
    )
    return numeric.join(labels).reset_index()


def holiday_names_by_date(raw: pd.DataFrame) -> pd.Series:
    """Ánh xạ ngày sang tên sự kiện, lấy từ nhãn lúc 00:00 trong CSV."""
    names = raw["holiday"].str.strip()
    events = pd.DataFrame(
        {"date": raw["date_time"].dt.normalize(), "holiday_name": names}
    ).loc[names.ne("None") & names.ne("")].drop_duplicates()
    if events["date"].duplicated().any():
        raise ValueError("Có ngày mang nhiều tên sự kiện.")
    return events.set_index("date")["holiday_name"]


def federal_holidays(start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    """Lịch lễ liên bang Mỹ (ngày nghỉ bù), biết trước và không phụ thuộc mục tiêu."""
    return USFederalHolidayCalendar().holidays(start, end, return_name=True)


def add_holiday_columns(
    table: pd.DataFrame, raw: pd.DataFrame, complete_holidays: bool = False
) -> pd.DataFrame:
    """Gắn holiday_name và is_holiday cho mọi giờ trong ngày có sự kiện.

    complete_holidays=True bổ sung các ngày lễ liên bang mà CSV không có nhãn
    vì thiếu đúng dòng 00:00.
    """
    names = holiday_names_by_date(raw)
    if complete_holidays:
        dates = table["date_time"].dt.normalize()
        calendar = federal_holidays(dates.min(), dates.max())
        names = names.combine_first(calendar)
    result = table.copy()
    mapped = result["date_time"].dt.normalize().map(names)
    result["holiday_name"] = mapped.fillna("None")
    result["is_holiday"] = mapped.notna().astype("int8")
    return result


def build_hourly_table(
    raw: pd.DataFrame,
    mask_stuck_temp: bool = False,
    complete_holidays: bool = False,
) -> pd.DataFrame:
    """Tạo bảng một dòng mỗi giờ quan sát, chưa điền thiếu và chưa chia tập."""
    target = build_hourly_target(raw)
    weather = build_hourly_weather(raw, mask_stuck_temp=mask_stuck_temp)
    table = target.merge(weather, on="date_time", how="outer", validate="one_to_one")
    if table["traffic_volume"].isna().any():
        raise ValueError("Bảng mục tiêu và bảng thời tiết chưa khớp timestamp.")
    return add_holiday_columns(table, raw, complete_holidays=complete_holidays)


def split_chronological(table: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Giữ điểm gọi hiện tại và dùng chung quy tắc chia theo thời gian."""
    return split_by_time(table)


def fill_missing_weather(splits: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Học median từ train và điền bằng quan sát gốc đã có theo thời gian."""
    statistics = fit_weather_fill(splits["train"])
    history = splits["train"][["date_time", "temp"]].iloc[:0].copy()
    filled = {}
    for name, part in splits.items():
        filled[name] = fill_weather(part, statistics, history=history)
        history = pd.concat([history, part[["date_time", "temp"]]], ignore_index=True)
    return filled


def load_hourly_splits(
    path: str | Path = DATA_PATH,
    mask_stuck_temp: bool = False,
    complete_holidays: bool = False,
) -> dict[str, pd.DataFrame]:
    """Đọc CSV, gộp theo giờ và chia theo thời gian trước khi điền thiếu."""
    raw = load_raw(path)
    table = build_hourly_table(
        raw, mask_stuck_temp=mask_stuck_temp, complete_holidays=complete_holidays
    )
    return split_chronological(table)


def load_splits(
    path: str | Path = DATA_PATH,
    mask_stuck_temp: bool = False,
    complete_holidays: bool = False,
) -> dict[str, pd.DataFrame]:
    """Chuẩn bị ba tập để huấn luyện cuối hoặc dự đoán sau khi đã chốt quy tắc."""
    return fill_missing_weather(load_hourly_splits(path, mask_stuck_temp, complete_holidays))
