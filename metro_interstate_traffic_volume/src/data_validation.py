"""Các kiểm tra dữ liệu trước khi tiền xử lý."""

import pandas as pd
import numpy as np


EXPECTED_COLUMNS = [
    "holiday",
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "weather_main",
    "weather_description",
    "date_time",
    "traffic_volume",
]


def validate_structure_and_time(df: pd.DataFrame) -> dict:
    """Kiểm tra cấu trúc và thời gian, trả về kết quả tóm tắt."""
    # Kiểm tra cấu trúc trước khi truy cập từng cột.
    if not df.columns.is_unique:
        raise ValueError("Dữ liệu có tên cột trùng.")

    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
    extra_columns = sorted(set(df.columns) - set(EXPECTED_COLUMNS))

    if missing_columns or extra_columns:
        raise ValueError(
            f"Cột thiếu: {missing_columns}. Cột ngoài dự kiến: {extra_columns}."
        )

    if df.empty:
        raise ValueError("Dữ liệu không có dòng.")

    # Parse trong biến riêng để giữ nguyên dữ liệu đầu vào.
    timestamps = pd.to_datetime(
        df["date_time"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",
    )

    if timestamps.isna().any():
        raise ValueError("Có timestamp bị thiếu.")

    if not timestamps.eq(timestamps.dt.floor("h")).all():
        raise ValueError("Có timestamp không nằm đúng đầu giờ.")

    # Thiếu mục tiêu cần được phát hiện trước khi kiểm tra nhóm.
    if df["traffic_volume"].isna().any():
        raise ValueError("Có traffic_volume bị thiếu.")

    if not pd.api.types.is_numeric_dtype(df["traffic_volume"]):
        raise ValueError("traffic_volume phải có kiểu số.")

    if not df["traffic_volume"].ge(0).all():
        raise ValueError("Có traffic_volume âm hoặc không hợp lệ.")

    # Mỗi giờ phải có đúng một giá trị mục tiêu phân biệt.
    traffic_counts = df.groupby(timestamps)["traffic_volume"].nunique()
    conflicting_times = traffic_counts[traffic_counts.ne(1)]

    if not conflicting_times.empty:
        raise ValueError(
            "Có timestamp mang nhiều giá trị traffic_volume: "
            f"{conflicting_times.index[:5].tolist()}"
        )

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "unique_timestamp_count": timestamps.nunique(),
        "conflicting_timestamp_count": len(conflicting_times),
        "start_time": timestamps.min(),
        "end_time": timestamps.max(),
        "is_time_sorted": timestamps.is_monotonic_increasing,
    }
def validate_final_splits(
    splits: dict[str, pd.DataFrame],
    hourly_target: pd.DataFrame,
) -> pd.DataFrame:
    """Kiểm tra ba tập cuối và đối chiếu toàn bộ thời gian, mục tiêu."""
    split_names = ("train", "validation", "test")

    if set(splits) != set(split_names):
        raise ValueError("Cần đúng ba tập train, validation và test.")

    required_columns = {
        "date_time",
        "traffic_volume",
        "temp_c",
        "rain_1h",
        "snow_1h",
        "clouds_all",
    }
    reference_columns = splits["train"].columns
    summary = []

    for split_name in split_names:
        part = splits[split_name]

        # Kiểm tra cấu trúc trước khi truy cập từng cột.
        if part.empty:
            raise ValueError(f"{split_name} không có dòng.")

        missing_columns = required_columns - set(part.columns)
        if missing_columns:
            raise ValueError(
                f"{split_name} thiếu cột: {sorted(missing_columns)}"
            )

        if "temp" in part.columns:
            raise ValueError(f"{split_name} vẫn còn cột temp Kelvin.")

        if not part.columns.is_unique:
            raise ValueError(f"{split_name} có tên cột trùng.")

        if not part.columns.equals(reference_columns):
            raise ValueError(f"{split_name} có tên hoặc thứ tự cột khác train.")

        if part.isna().any().any():
            raise ValueError(f"{split_name} còn giá trị thiếu.")

        # Kiểm tra thời gian trong từng tập.
        timestamps = part["date_time"]
        if not pd.api.types.is_datetime64_any_dtype(timestamps):
            raise ValueError(f"{split_name}: date_time phải là datetime.")

        if not timestamps.is_unique or not timestamps.is_monotonic_increasing:
            raise ValueError(f"{split_name} có timestamp lặp hoặc sai thứ tự.")

        # Ngoài khóa thời gian, các cột phải là số hữu hạn.
        numeric_data = part.drop(columns="date_time")
        if numeric_data.select_dtypes(include="number").shape[1] != (
            numeric_data.shape[1]
        ):
            raise ValueError(f"{split_name} còn cột ngoài thời gian chưa là số.")

        if not np.isfinite(numeric_data.to_numpy()).all():
            raise ValueError(f"{split_name} có giá trị số vô hạn.")

        # Kiểm tra miền giá trị đã dùng ở Bước 10.
        for column in ("traffic_volume", "rain_1h", "snow_1h"):
            if not part[column].ge(0).all():
                raise ValueError(f"{split_name}: {column} có giá trị âm.")

        if not part["clouds_all"].between(0, 100).all():
            raise ValueError(f"{split_name}: clouds_all nằm ngoài 0–100.")

        summary.append({
            "tap": split_name,
            "so_dong": len(part),
            "so_cot": part.shape[1],
            "so_o_thieu": int(part.isna().sum().sum()),
            "tu_gio": timestamps.min(),
            "den_gio": timestamps.max(),
        })

    # Kiểm tra ranh giới giữa các tập.
    if not (
        splits["train"]["date_time"].max()
        < splits["validation"]["date_time"].min()
        and splits["validation"]["date_time"].max()
        < splits["test"]["date_time"].min()
    ):
        raise ValueError("Ranh giới thời gian giữa ba tập không hợp lệ.")

    # Đối chiếu cả timestamp và lưu lượng với bảng mục tiêu theo giờ.
    target_columns = ["date_time", "traffic_volume"]
    actual_target = (
        pd.concat(
            [splits[name][target_columns] for name in split_names],
            ignore_index=True,
        )
        .sort_values("date_time")
        .reset_index(drop=True)
    )
    expected_target = (
        hourly_target[target_columns]
        .sort_values("date_time")
        .reset_index(drop=True)
    )

    if not actual_target.equals(expected_target):
        raise ValueError(
            "Thời gian hoặc traffic_volume không khớp bảng mục tiêu theo giờ."
        )

    return pd.DataFrame(summary)