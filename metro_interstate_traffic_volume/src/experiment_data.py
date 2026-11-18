"""Cổng đọc dữ liệu chung cho notebook thực nghiệm, không xuất lại CSV.

processed là snapshot bàn giao; raw giữ thiếu để fit preprocessing trong CV;
filled giữ schema nhãn của raw và điền thời tiết chỉ bằng thống kê train.
Mọi chế độ dùng cùng timestamp/target của snapshot processed hiện có.
"""

from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from src.data import DATA_PATH, PROJECT_DIR, fill_missing_weather, load_hourly_splits


def _validate_splits(splits: dict[str, pd.DataFrame]) -> None:
    """Từ chối dữ liệu rỗng, sai khóa thời gian, target hoặc schema giữa các tập."""
    previous_end = None
    columns = None
    for name, frame in splits.items():
        required = {"date_time", "traffic_volume"}
        if not required.issubset(frame.columns) or frame.empty:
            raise ValueError(f"{name}: cần dữ liệu có date_time và traffic_volume.")
        if not frame.columns.is_unique:
            raise ValueError(f"{name}: tên cột bị trùng.")
        times = frame["date_time"]
        if not pd.api.types.is_datetime64_any_dtype(times):
            raise ValueError(f"{name}: date_time phải là datetime.")
        if times.isna().any() or not times.is_unique or not times.is_monotonic_increasing:
            raise ValueError(f"{name}: timestamp phải đầy đủ, duy nhất và tăng dần.")
        target = frame["traffic_volume"]
        if not pd.api.types.is_numeric_dtype(target) or not np.isfinite(target).all():
            raise ValueError(f"{name}: traffic_volume phải là số hữu hạn.")
        if target.lt(0).any():
            raise ValueError(f"{name}: traffic_volume không được âm.")
        if columns is not None and not columns.equals(frame.columns):
            raise ValueError(f"{name}: schema không khớp train.")
        if previous_end is not None and times.iloc[0] <= previous_end:
            raise ValueError(f"{name}: các tập bị chồng lấn hoặc sai thứ tự thời gian.")
        columns = frame.columns
        previous_end = times.iloc[-1]


def _read_processed(project_dir: Path, names: tuple[str, ...]) -> dict[str, pd.DataFrame]:
    result = {}
    for name in names:
        path = project_dir / "data" / "processed" / f"{name}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Thiếu snapshot {path}; không tự dựng lại hoặc ghi đè CSV.")
        result[name] = pd.read_csv(path, parse_dates=["date_time"])
    _validate_splits(result)
    return result


def load_experiment_splits(
    path: str | Path | None = None,
    *,
    project_dir: str | Path | None = None,
    stage: Literal["processed", "raw", "filled"] = "processed",
    include_test: bool = False,
    mask_stuck_temp: bool = False,
    complete_holidays: bool = False,
) -> dict[str, pd.DataFrame]:
    """Đọc cùng bộ chia train/validation cho mọi thí nghiệm.

    stage="processed" đọc CSV bàn giao và không học lại preprocessing.
    stage="raw" trả bảng theo giờ trước imputation để mỗi CV fold tự fit.
    stage="filled" giữ schema raw và điền thời tiết từ train; không dùng nó
    thay raw trong CV. Hai chế độ raw/filled đối chiếu timestamp và target
    với processed, dừng nếu nguồn gốc hoặc mốc chia đã thay đổi.

    Mặc định không trả test. include_test=True chỉ dùng khi notebook cần
    metadata ranh giới hoặc khi đã được phép đánh giá cuối; hàm không fit,
    dự đoán, chấm điểm, fallback nguồn hay ghi bất kỳ file dữ liệu nào.
    """
    root = Path(project_dir).resolve() if project_dir is not None else PROJECT_DIR
    if stage not in {"processed", "raw", "filled"}:
        raise ValueError(f"stage không hỗ trợ: {stage!r}.")
    if stage == "processed" and (path is not None or mask_stuck_temp or complete_holidays):
        raise ValueError("processed dùng snapshot đã có; đổi cleaning/path cần chọn raw hoặc filled.")
    names = ("train", "validation", "test") if include_test else ("train", "validation")
    snapshot = _read_processed(root, names)
    if stage == "processed":
        return snapshot

    source = Path(path) if path is not None else root / "data" / DATA_PATH.name
    if not source.is_absolute():
        source = root / source
    hourly = load_hourly_splits(
        path=source,
        mask_stuck_temp=mask_stuck_temp,
        complete_holidays=complete_holidays,
    )
    result = {name: hourly[name].reset_index(drop=True) for name in names}
    _validate_splits(result)
    for name, frame in result.items():
        expected = snapshot[name][["date_time", "traffic_volume"]].reset_index(drop=True)
        actual = frame[["date_time", "traffic_volume"]]
        try:
            pd.testing.assert_frame_equal(actual, expected, check_dtype=False, check_exact=True)
        except AssertionError as exc:
            raise ValueError(
                f"{name}: timestamp/target của raw khác snapshot processed; "
                "không trộn hai phiên bản dữ liệu trong một đối chứng."
            ) from exc
    return fill_missing_weather(result) if stage == "filled" else result
