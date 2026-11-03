"""Lưu nhật ký thí nghiệm dạng văn bản, mỗi lần chạy một file riêng."""

from collections.abc import Mapping, Sequence
from datetime import date, datetime, timedelta, timezone
from math import isclose, isfinite
from pathlib import Path
import re


DEFAULT_LOG_DIR = Path(__file__).resolve().parents[1] / "experiments"


def save_experiment_log(
    *,
    model: str,
    features: Sequence[str],
    results: Mapping[str, float],
    observations: Sequence[str],
    problems: Sequence[str],
    next_steps: Sequence[str],
    dataset: str = "Traffic Volume",
    data_split: Mapping[str, float] | None = None,
    split_strategy: str = "Chronological",
    experiment_date: date | str | None = None,
    output_dir: str | Path = DEFAULT_LOG_DIR,
) -> Path:
    """Ghi EXP_001.txt, EXP_002.txt... và trả về đường dẫn tuyệt đối.

    results nhận MAE, RMSE và R2 (hoặc R²). data_split nhận phần trăm
    Train/Validation/Test, mặc định 70/15/15. Ngày mặc định theo UTC+7.
    Danh sách ghi chú rỗng được ghi là "Chưa ghi nhận". File đã tồn tại
    không bị ghi đè; ID được cấp theo file EXP_<số>.txt trong output_dir.
    """
    def single_line(value: str, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} phải là chuỗi không rỗng.")
        if "\n" in value or "\r" in value:
            raise ValueError(f"{field} phải nằm trên một dòng.")
        return value.strip()

    def bullet_lines(items: Sequence[str], field: str) -> str:
        if isinstance(items, str):
            raise TypeError(f"{field} phải là danh sách chuỗi, ví dụ ['Ghi chú'].")
        return "\n".join(
            f"- {single_line(item, field)}" for item in items
        ) or "- Chưa ghi nhận"

    model = single_line(model, "model")
    dataset = single_line(dataset, "dataset")
    split_strategy = single_line(split_strategy, "split_strategy")
    if not features:
        raise ValueError("features cần có ít nhất một đặc trưng.")
    feature_text = bullet_lines(features, "features")
    observation_text = bullet_lines(observations, "observations")
    problem_text = bullet_lines(problems, "problems")
    next_step_text = bullet_lines(next_steps, "next_steps")

    split = dict(data_split) if data_split is not None else {
        "Train": 70, "Validation": 15, "Test": 15,
    }
    if set(split) != {"Train", "Validation", "Test"}:
        raise ValueError("data_split cần đúng ba khóa Train, Validation, Test.")
    percentages = [float(split[key]) for key in ("Train", "Validation", "Test")]
    if not all(isfinite(x) and 0 < x < 100 for x in percentages):
        raise ValueError("Tỷ lệ chia phải hữu hạn và nằm giữa 0 và 100.")
    if not isclose(sum(percentages), 100, abs_tol=1e-6):
        raise ValueError("Tổng tỷ lệ Train/Validation/Test phải bằng 100%.")

    mae = float(results["MAE"])
    rmse = float(results["RMSE"])
    r2 = float(results["R2"] if "R2" in results else results["R²"])
    if not all(isfinite(x) for x in (mae, rmse, r2)):
        raise ValueError("Metrics phải là các số hữu hạn.")
    if mae < 0 or rmse < 0:
        raise ValueError("MAE và RMSE không được âm.")

    if experiment_date is None:
        run_date = datetime.now(timezone(timedelta(hours=7))).date()
    elif isinstance(experiment_date, datetime):
        run_date = experiment_date.date()
    elif isinstance(experiment_date, date):
        run_date = experiment_date
    else:
        run_date = date.fromisoformat(experiment_date)

    directory = Path(output_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    existing_ids = [
        int(match.group(1))
        for path in directory.iterdir()
        if (match := re.fullmatch(r"EXP_(\d+)\.txt", path.name))
    ]
    number = max(existing_ids, default=0) + 1
    while True:
        experiment_id = f"EXP_{number:03d}"
        text = (
            f"Experiment ID: {experiment_id}\n"
            f"Date: {run_date.isoformat()}\n\n"
            f"Dataset: {dataset}\n"
            f"Model: {model}\n\n"
            f"Features:\n{feature_text}\n\n"
            f"Data Split:\n"
            f"- Train: {percentages[0]:g}%\n"
            f"- Validation: {percentages[1]:g}%\n"
            f"- Test: {percentages[2]:g}%\n"
            f"- Split strategy: {split_strategy}\n\n"
            f"Results:\n- MAE: {mae!r}\n- RMSE: {rmse!r}\n- R²: {r2!r}\n\n"
            f"Observations:\n{observation_text}\n\n"
            f"Problems:\n{problem_text}\n\n"
            f"Next Steps:\n{next_step_text}\n"
        )
        path = directory / f"{experiment_id}.txt"
        try:
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
            return path
        except FileExistsError:
            number += 1
