"""Chạy pipeline chuẩn bị dữ liệu từ CSV gốc."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from . import data_validation, features, preprocessing


def prepare_data(project_dir: Path) -> pd.DataFrame:
    """Chuẩn bị, kiểm tra và xuất ba tập dữ liệu."""
    data_path = project_dir / "data" / "Metro_Interstate_Traffic_Volume.csv"
    output_dir = project_dir / "data" / "processed"
    split_names = ("train", "validation", "test")

    # Giữ nguyên chuỗi 'None' trong cột holiday.
    raw_data = pd.read_csv(data_path, keep_default_na=False)

    # Tạo một dòng mục tiêu và thời tiết cho mỗi giờ quan sát.
    hourly_target = preprocessing.build_hourly_target(raw_data)
    hourly_weather = preprocessing.build_hourly_weather(raw_data)
    hourly_data = preprocessing.merge_hourly_data(
        hourly_target,
        hourly_weather,
    )

    # Gắn nhãn sự kiện theo ngày và chia theo thời gian.
    hourly_with_holiday = features.add_holiday_features(
        hourly_data,
        raw_data,
    )
    raw_splits = preprocessing.split_by_time(hourly_with_holiday)

    # Chỉ học thống kê điền thiếu từ train.
    fill_statistics = preprocessing.fit_weather_fill(
        raw_splits["train"]
    )

    featured_splits = {}
    history = raw_splits["train"][["date_time", "temp"]].iloc[:0].copy()

    for split_name in split_names:
        original = raw_splits[split_name]

        filled = preprocessing.fill_weather(
            original,
            fill_statistics,
            history=history,
        )
        featured_splits[split_name] = (
            features.add_time_temperature_features(filled)
        )

        # Lưu lịch sử quan sát gốc, trước khi điền thiếu.
        history = pd.concat(
            [history, original[["date_time", "temp"]]],
            ignore_index=True,
        )

    # Chỉ học danh sách nhãn phân loại từ train.
    vocabularies = features.fit_category_vocabulary(
        featured_splits["train"]
    )

    final_splits = {}
    for split_name in split_names:
        encoded = features.encode_categories(
            featured_splits[split_name],
            vocabularies,
        )
        final_splits[split_name] = features.select_final_columns(encoded)

    # Kiểm tra toàn bộ kết quả trước khi xuất.
    summary = data_validation.validate_final_splits(
        final_splits,
        hourly_target,
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    # Viết đủ ba CSV vào thư mục tạm trước khi đưa vào vị trí bàn giao.
    with TemporaryDirectory(
        prefix=".prepare_data_",
        dir=output_dir,
    ) as temporary_dir:
        staging_dir = Path(temporary_dir)

        for split_name in split_names:
            final_splits[split_name].to_csv(
                staging_dir / f"{split_name}.csv",
                index=False,
                encoding="utf-8",
                date_format="%Y-%m-%d %H:%M:%S",
            )

        for split_name in split_names:
            (staging_dir / f"{split_name}.csv").replace(
                output_dir / f"{split_name}.csv"
            )

    return summary


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parents[1]
    result = prepare_data(project_dir)

    print(result.to_string(index=False))
    print("Đã xuất train.csv, validation.csv và test.csv vào data/processed/.")
