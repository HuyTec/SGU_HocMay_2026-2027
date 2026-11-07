"""Lưu và đọc kết quả thí nghiệm theo từng workbook."""

import hashlib
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from math import isfinite
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4


WORKBOOK_NAME = "experiments_logs.xlsx"
DATA_LOCATION = "I-94 hướng Tây, trạm MnDOT ATR 301, Minneapolis–St. Paul, Minnesota, Mỹ"
DATA_TIME_ZONE = "CST theo nguồn UCI"
DATA_SOURCE_URL = "https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume"
VERSIONS = ("V_1", "V_2", "V_3", "V_4")
PRIOR_VERSION = {"V_3": "V_2", "V_4": "V_3"}


def _sheet_name(version, title):
    return f"{version.replace('_', '')} {title}"


def _read_guide(book, version):
    name = _sheet_name(version, "Hướng dẫn")
    return {key: value for key, value in book[name].values if key is not None} if name in book.sheetnames else {}


def _check_provenance(book, version, digest):
    """Từ chối kết quả cũ khi phiên bản đối chứng đã chạy lại."""
    guide = _read_guide(book, version)
    if not guide:
        raise FileNotFoundError(f"Chưa có kết quả {version} trong {WORKBOOK_NAME}.")
    if guide.get("SHA-256 CSV") != digest:
        raise ValueError(f"Kết quả {version} dùng CSV khác. Hãy chạy lại {version}.")
    parent = PRIOR_VERSION.get(version)
    if parent:
        previous = _check_provenance(book, parent, digest)
        if guide.get("Mã chạy đối chứng") != previous.get("Mã lần chạy"):
            raise ValueError(f"{version} tham chiếu một lần chạy {parent} khác. Hãy chạy lại {version}.")
    return guide


COMBINED_GUIDES = {
    "Validation": "Mỗi dòng là một mô hình hoặc baseline thứ–giờ. Giảm MAE dương nghĩa là mô hình vượt baseline.",
    "Hyper Parameters": "Mỗi dòng là một tham số thực tế của mô hình cuối. Cột Nguồn cho biết tham số cố định hay đã tuning.",
    "Tuning CV": "Mỗi dòng là một ứng viên. MAE từng fold dùng để chọn tham số. Hạng 1 có MAE CV thấp nhất.",
    "Evaluation": "Chỉ so trực tiếp trong cùng nhóm giờ chấm. Xem số giờ train và mốc CST khi diễn giải kết quả.",
}


def _table_bounds(tab):
    """Tìm vùng dữ liệu khi Excel đã bỏ bộ lọc."""
    from openpyxl.utils import range_boundaries

    if tab.auto_filter.ref:
        _, _, width, end = range_boundaries(tab.auto_filter.ref)
        return width, end
    width = 0
    for cell in tab[1]:
        if cell.value is None:
            break
        width += 1
    end = 1
    last_row = tab.max_row
    while end < last_row:
        value = tab.cell(end + 1, 1).value
        if value is None or (isinstance(value, str) and value.startswith("Cách đọc ·")):
            break
        end += 1
    return width, end


def _write_table(tab, headers, rows, widths, notes=None, guide=None):
    """Cập nhật vùng bảng và giữ nguyên định dạng của sheet hiện có."""
    from copy import copy
    from openpyxl.comments import Comment
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    count = len(headers)
    last_column = get_column_letter(count)
    old_width, old_end = _table_bounds(tab)
    if guide:
        # Tìm chú thích theo chính nội dung và ô gộp, kể cả khi bộ lọc bị tắt.
        old_guides = [
            area for area in tab.merged_cells.ranges
            if area.min_col == 1 and area.min_row == area.max_row
            and isinstance(tab.cell(area.min_row, 1).value, str)
            and tab.cell(area.min_row, 1).value.startswith("Cách đọc ·")
        ]
        if old_guides:
            for area in old_guides:
                tab.unmerge_cells(str(area))
                tab.cell(area.min_row, 1).value = None
        elif isinstance(tab.cell(old_end + 2, 1).value, str) and tab.cell(old_end + 2, 1).value.startswith("Cách đọc ·"):
            tab.cell(old_end + 2, 1).value = None
        elif tab.cell(5, 1).value == "Chưa có kết quả":
            if "A3:G3" in tab.merged_cells:
                tab.unmerge_cells("A3:G3")
            tab.cell(3, 1).value = None
            tab.cell(5, 1).value = None

    for col, (header, width) in enumerate(zip(headers, widths), start=1):
        cell = tab.cell(1, col)
        cell.value = header
        if not cell.has_style:
            cell.fill = PatternFill("solid", fgColor="1F4058")
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(vertical="center", wrap_text=True)
        if notes and header in notes and cell.comment is None:
            cell.comment = Comment(notes[header], "Dự án Metro")
        letter = get_column_letter(col)
        if letter not in tab.column_dimensions:
            tab.column_dimensions[letter].width = width

    end = 1
    for end, row in enumerate(rows, start=2):
        for col, value in enumerate(row, start=1):
            cell = tab.cell(end, col)
            if not cell.has_style and end > 2:
                cell._style = copy(tab.cell(2, col)._style)
            if not cell.has_style:
                cell.alignment = Alignment(vertical="center", wrap_text=True)
                if isinstance(value, float):
                    cell.number_format = "0.0000"
            cell.value = value
            if cell.data_type == "f" and isinstance(value, str):
                cell.data_type = "s"
    if old_end > end:
        for row in tab.iter_rows(min_row=end + 1, max_row=old_end, max_col=old_width):
            for cell in row:
                cell.value = None
    if old_width > count:
        for row in tab.iter_rows(max_row=min(old_end, end), min_col=count + 1, max_col=old_width):
            for cell in row:
                cell.value = None
    tab.auto_filter.ref = f"A1:{last_column}{end}"
    if not tab.freeze_panes:
        tab.freeze_panes = "B2"
    if tab.row_dimensions[1].height is None:
        tab.row_dimensions[1].height = 32

    if guide:
        row = end + 2
        tab.merge_cells(start_row=row, start_column=1, end_row=row, end_column=count)
        cell = tab.cell(row, 1, f"Cách đọc · {guide}")
        cell.fill = PatternFill("solid", fgColor="EFF4F7")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        tab.row_dimensions[row].height = 30
        tab.sheet_view.showGridLines = False
    return tab


def _save_workbook(book, path):
    """Ghi bản hoàn chỉnh trước khi thay file đích."""
    with TemporaryDirectory(prefix=".excel_", dir=path.parent) as temporary:
        staged = Path(temporary) / path.name
        book.save(staged)
        try:
            staged.replace(path)
        except PermissionError as error:
            raise PermissionError(f"Không ghi được {path}. Hãy đóng file trong Excel rồi chạy lại cell lưu.") from error


def save_experiment_workbook(
    *, version, results, target, splits, folds, data_path, output_dir,
    baseline_metrics=None, baseline_predictions=None, comparisons=None, prior_run=None,
    train_sizes=None, baseline_train_size=None,
):
    """Lưu điểm, dự đoán và nguồn đối chứng của một lần chạy."""
    if not re.fullmatch(r"V_[1-4]", version):
        raise ValueError(f"Phiên bản workbook không hợp lệ: {version}")
    if target.empty or not target["date_time"].is_unique or not target["date_time"].is_monotonic_increasing:
        raise ValueError("Validation phải có giờ duy nhất và tăng dần.")
    if (baseline_metrics is None) != (baseline_predictions is None):
        raise ValueError("Cần cả điểm và dự đoán baseline, hoặc bỏ cả hai.")
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment

    def text_json(value):
        return json.dumps(value, ensure_ascii=False, default=str)

    written = set()

    def sheet(title, headers, rows, widths, notes=None, *, overview=False, combined=False):
        name = title if overview or combined else _sheet_name(version, title)
        written.add(name)
        tab = book[name] if name in book.sheetnames else book.create_sheet(name, 0 if overview else None)
        return _write_table(tab, headers, rows, widths, notes, COMBINED_GUIDES.get(title) if combined else None)

    output_dir = Path(output_dir)
    data_path = Path(data_path)
    now = datetime.now(timezone(timedelta(hours=7)))
    try:
        git = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=data_path.resolve().parent,
            capture_output=True, text=True, check=False,
        )
        revision = git.stdout.strip() if git.returncode == 0 else "Không xác định"
    except OSError:
        revision = "Không xác định"
    prefix = version.replace("_", "")
    run_id = f"{prefix}_{now:%Y%m%d_%H%M%S}_{uuid4().hex[:8]}"
    digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
    path = output_dir / WORKBOOK_NAME
    if path.is_file():
        with path.open("rb") as stream:
            book = load_workbook(stream)
    else:
        book = Workbook()
        book.remove(book.active)
    parent = PRIOR_VERSION.get(version)
    if parent:
        guide = _check_provenance(book, parent, digest)
        if prior_run != guide.get("Mã lần chạy"):
            raise ValueError(f"{parent} đã thay đổi sau khi đọc. Hãy chạy lại phép đối chứng.")
    predictions = target[["date_time", "traffic_volume"]].reset_index(drop=True).copy()
    sample_hash = hashlib.sha256(predictions.to_csv(index=False).encode("utf-8")).hexdigest()
    rows, cv_rows, parameter_rows = [], [], []
    train_sizes = train_sizes or {}
    n_train = len(splits["train"])
    baseline_mae = None
    if baseline_metrics is not None:
        baseline_mae = float(baseline_metrics["MAE"])
        predictions["Baseline|Trung bình thứ–giờ"] = baseline_predictions
        rows.append((
            "Baseline", "Trung bình thứ–giờ", "day_of_week, hour", len(target),
            baseline_mae, float(baseline_metrics["RMSE"]), float(baseline_metrics["R2"]),
            0.0, None, None, baseline_train_size if baseline_train_size is not None else n_train,
        ))

    from src.models import input_columns
    for item in results:
        config, model = item["config"], item["model"]
        key = f"{config}|{model}"
        if key in predictions:
            raise ValueError(f"Kết quả bị trùng: {key}")
        predictions[key] = item["prediction"]
        search, metrics = item["search"], item["metrics"]
        mae = float(metrics["MAE"])
        rows.append((
            config, model, ", ".join(input_columns(model, item["features"])),
            len(target), mae, float(metrics["RMSE"]), float(metrics["R2"]),
            None if baseline_mae is None else baseline_mae - mae,
            float(-search.best_score_), text_json(search.best_params_), train_sizes.get(config, n_train),
        ))
        estimator = search.best_estimator_
        steps = getattr(estimator, "steps", None)
        final_model = steps[-1][1] if steps else estimator
        tuned = {name.rsplit("__", 1)[-1] for name in search.best_params_}
        for name, value in sorted(final_model.get_params(deep=False).items()):
            if not isinstance(value, (bool, int, str)) and not (isinstance(value, float) and isfinite(value)):
                value = text_json(value)
            parameter_rows.append((config, model, name, value, "Được tuning" if name in tuned else "Cố định"))
        for candidate in search.scores.to_dict("records"):
            cv_rows.append((
                config, model, int(candidate["rank"]), text_json(candidate["parameters"]),
                *[float(candidate[f"fold_{i}_mae"]) for i in range(1, len(folds[config]) + 1)],
                float(candidate["mean_cv_mae"]),
            ))
    fold_count = len(next(iter(folds.values())))
    if any(len(frame) != fold_count for frame in folds.values()):
        raise ValueError("Các cấu hình phải có cùng số fold trong một workbook.")
    rows.sort(key=lambda row: row[4])

    validation = sheet(
        "Validation",
        ["Cấu hình", "Mô hình", "Cột trước mã hóa", "Số giờ", "MAE", "RMSE", "R²",
         "Giảm MAE so baseline", "MAE CV", "Tham số đã chọn", "Giờ train"],
        rows, [16, 27, 28, 10, 14, 14, 12, 17, 14, 46, 13],
        {
            "MAE": "Sai số tuyệt đối trung bình, đơn vị xe/giờ. Thấp hơn tốt hơn trên cùng tập giờ.",
            "RMSE": "Sai số căn quân phương, đơn vị xe/giờ. Phạt mạnh hơn các lỗi lớn.",
            "R²": "Hệ số xác định. Cao hơn tốt hơn khi so trên cùng tập giờ.",
            "Giảm MAE so baseline": "MAE baseline trừ MAE mô hình. Số dương là mô hình giảm sai số.",
            "MAE CV": "MAE trung bình trên các fold nằm bên trong train. Để trống với baseline.",
            "Cột trước mã hóa": "Tên cột đưa vào pipeline. Ridge mã hóa one-hot cặp thứ–giờ.",
            "Tham số đã chọn": "Tham số có MAE CV thấp nhất. {} là mô hình chạy cấu hình mặc định.",
        },
    )
    for row in range(2, validation.max_row + 1):
        if validation.row_dimensions[row].height is None:
            validation.row_dimensions[row].height = 50
    sheet(
        "Hyper Parameters", ["Cấu hình", "Mô hình", "Tham số", "Giá trị sau fit", "Nguồn"],
        parameter_rows, [24, 25, 30, 40, 19],
        {"Giá trị sau fit": "Giá trị thực tế của mô hình cuối. Không gồm hệ số học được."},
    )
    cv = sheet(
        "Tuning CV",
        ["Cấu hình", "Mô hình", "Hạng", "Tham số",
         *[f"MAE fold {i}" for i in range(1, fold_count + 1)], "MAE CV"],
        cv_rows, [16, 26, 9, 60, *([14] * fold_count), 14],
        {"Hạng": "Xếp theo MAE CV trong cùng mô hình và cấu hình. Hạng 1 là thấp nhất."},
    )
    for row in range(2, cv.max_row + 1):
        if cv.row_dimensions[row].height is None:
            cv.row_dimensions[row].height = 45

    sheet(
        "Mốc dữ liệu",
        ["Tập", "Số giờ", "Bắt đầu", "Kết thúc", "Vai trò"],
        [(name, len(part), str(part["date_time"].min()), str(part["date_time"].max()), role)
         for name, part, role in (
             ("Train", splits["train"], "Fit mô hình và chia fold CV"),
             ("Validation gốc", splits["validation"], "Tập validation theo ranh giới chung"),
             ("Validation đã chấm", target, "Các giờ dùng để tính điểm trong workbook"),
             ("Test", splits["test"], "Giữ riêng, chưa chấm điểm"),
         )],
        [16, 12, 25, 25, 44],
    )
    sheet(
        "Mốc fold",
        ["Cấu hình", "Fold", "Fit từ", "Fit đến", "Chấm từ", "Chấm đến", "Giờ fit", "Giờ chấm"],
        [(config, int(row.fold), str(row.fit_start), str(row.fit_end), str(row.validation_start),
          str(row.validation_end), int(row.n_fit), int(row.n_validation))
         for config, frame in folds.items() for row in frame.itertuples(index=False)],
        [22, 10, 25, 25, 25, 25, 12, 12],
    )
    guide = sheet(
        "Hướng dẫn",
        ["Mục", "Giải thích"],
        [
            ("Mã lần chạy", run_id),
            ("Thời điểm (UTC+7)", now.strftime("%Y-%m-%d %H:%M:%S")),
            ("Nguồn", f"notebooks/experiments/{version}.ipynb"),
            ("Mã chạy đối chứng", prior_run),
            ("Commit gốc", revision + " (lần chạy có thể gồm thay đổi local)"),
            ("CSV đầu vào", data_path.name),
            ("Nguồn dữ liệu", DATA_SOURCE_URL),
            ("Địa điểm đo", DATA_LOCATION),
            ("Múi giờ quan sát", DATA_TIME_ZONE + ". Giữ nguyên timestamp trong CSV."),
            ("Giờ chấm từ (CST)", str(target["date_time"].min())),
            ("Giờ chấm đến (CST)", str(target["date_time"].max())),
            ("SHA-256 CSV", digest),
            ("SHA-256 giờ chấm", sample_hash),
            ("Đọc bảng Validation", "Các dòng được sắp theo MAE. So sánh trên cùng các giờ validation. Xem chú thích ở tiêu đề cột."),
            ("So với baseline", "Cột Giảm MAE so baseline dương khi mô hình giảm sai số, âm khi mô hình kém hơn baseline."),
            ("Đọc bảng Tuning CV", "Mỗi dòng là một ứng viên. MAE từng fold dùng để chọn tham số trong train."),
            ("Kiểm tra mốc", "Mốc fold thuộc train. Mốc dữ liệu tách train, validation và test theo thời gian."),
            ("Phạm vi", "Điểm chỉ đại diện cho các giờ trong sheet Dự đoán. Test được giữ riêng."),
            ("Đơn vị", "MAE và RMSE tính bằng xe/giờ. R² không có đơn vị."),
        ],
        [25, 104],
    )
    for row in range(2, guide.max_row + 1):
        if guide.row_dimensions[row].height is None:
            guide.row_dimensions[row].height = 30

    # Giữ đầy đủ độ chính xác để notebook sau có thể chấm lại cùng các giờ.
    predictions["date_time"] = predictions["date_time"].astype(str)
    sheet("Dự đoán", list(predictions.columns), predictions.itertuples(index=False, name=None),
          [24, 18] + [30] * (len(predictions.columns) - 2),
          {"traffic_volume": "Lưu lượng quan sát thật, đơn vị xe/giờ."})
    for title, frame in (comparisons or {}).items():
        clean = frame.astype(object).where(frame.notna(), None)
        sheet(title, list(clean.columns), clean.itertuples(index=False, name=None),
              [min(38, max(17, len(str(name)) + 2)) for name in clean.columns])

    overview_rows = []
    for current in VERSIONS:
        current_guide = _read_guide(book, current)
        if not current_guide:
            state = "Chưa có kết quả"
        else:
            try:
                _check_provenance(book, current, digest)
                state = "Sẵn sàng"
            except (ValueError, FileNotFoundError):
                state = "Cần chạy lại"
        overview_rows.append((
            current.replace("_", ""), state, current_guide.get("Mã lần chạy"),
            current_guide.get("Mã chạy đối chứng"),
        ))
    overview = sheet("Tổng quan", ["Phiên bản", "Trạng thái", "Mã lần chạy", "Mã chạy đối chứng"],
                     overview_rows, [18, 24, 38, 38], overview=True)
    overview["A7"] = "Mỗi phiên bản lưu lần chạy mới nhất. Chạy V2 → V3 → V4 để cập nhật chuỗi đối chứng."
    overview.merge_cells("A7:D7")
    for row, message in (
        (9, f"Địa điểm đo: {DATA_LOCATION}."),
        (10, f"Mốc dữ liệu và fold: {DATA_TIME_ZONE}. Thời điểm chạy: UTC+7."),
        (11, f"Nguồn: {DATA_SOURCE_URL}"),
    ):
        overview.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        overview.cell(row, 1, message).alignment = Alignment(wrap_text=True, vertical="center")
        overview.row_dimensions[row].height = 26

    # Các sheet chung chỉ tổng hợp các phiên bản có dữ liệu đã ghi.
    metric_rows, all_parameters, all_tuning, evaluation = [], [], [], []
    state_by_version = {label: state for label, state, _, _ in overview_rows}
    for current in VERSIONS:
        label = current.replace("_", "")
        status = state_by_version[label]
        info = _read_guide(book, current)
        if not info:
            continue
        result_rows = iter(book[_sheet_name(current, "Validation")].values)
        columns = next(result_rows)
        for values in result_rows:
            if values[0] is None:
                continue
            row = dict(zip(columns, values))
            metric_rows.append((
                label, status, row["Cấu hình"], row["Mô hình"], row.get("Giờ train"), row["Số giờ"],
                row["MAE"], row["RMSE"], row["R²"], row["Giảm MAE so baseline"], row["MAE CV"],
                row["Tham số đã chọn"],
            ))
            if status == "Sẵn sàng":
                sample = info.get("SHA-256 giờ chấm")
                # Hash gắn với cả nguồn CSV lẫn chính các giờ và mục tiêu được chấm.
                group = hashlib.sha256((info["SHA-256 CSV"] + sample).encode()).hexdigest()[:10] if sample else None
                evaluation.append((
                    group or f"{label} · chưa có mã giờ", label, row["Cấu hình"], row["Mô hình"],
                    row.get("Giờ train"), row["Số giờ"], row["MAE"], row["RMSE"], row["R²"],
                    row["Giảm MAE so baseline"], info["Mã lần chạy"],
                    info.get("Giờ chấm từ (CST)"), info.get("Giờ chấm đến (CST)"),
                    info.get("Địa điểm đo", DATA_LOCATION),
                ))
        parameters_tab = _sheet_name(current, "Hyper Parameters")
        if parameters_tab in book.sheetnames:
            all_parameters.extend((label, status, *values) for values in book[parameters_tab].values if values[0] not in (None, "Cấu hình"))
        all_tuning.extend((label, status, *values) for values in book[_sheet_name(current, "Tuning CV")].values if values[0] not in (None, "Cấu hình"))

    metric_notes = {
        "MAE": "Sai số tuyệt đối trung bình, xe/giờ. Thấp hơn tốt hơn trên cùng các giờ chấm.",
        "RMSE": "Sai số căn quân phương, xe/giờ. Nhạy hơn với các sai số lớn.",
        "Giảm MAE": "MAE baseline thứ–giờ của phiên bản trừ MAE mô hình trên cùng giờ chấm.",
        "MAE CV": "Điểm trong train để chọn tham số. Điểm validation nằm ở cột MAE.",
    }
    sheet("Validation",
          ["Phiên bản", "Trạng thái", "Cấu hình", "Mô hình", "Giờ train", "Giờ chấm", "MAE", "RMSE", "R²",
           "Giảm MAE", "MAE CV", "Tham số đã chọn"],
          metric_rows, [13, 20, 24, 26, 13, 13, 14, 14, 12, 15, 14, 48], metric_notes, combined=True)
    sheet("Hyper Parameters", ["Phiên bản", "Trạng thái", "Cấu hình", "Mô hình", "Tham số", "Giá trị sau fit", "Nguồn"],
          all_parameters, [13, 20, 24, 26, 30, 38, 18],
          {"Nguồn": "Được tuning: xuất hiện trong bộ tham số được chọn. Cố định: lấy từ cấu hình mô hình."}, combined=True)
    sheet("Tuning CV", ["Phiên bản", "Trạng thái", "Cấu hình", "Mô hình", "Hạng", "Tham số",
                         *[f"MAE fold {i}" for i in range(1, fold_count + 1)], "MAE CV"],
          all_tuning, [13, 20, 24, 26, 10, 58, *([14] * fold_count), 14],
          {"Hạng": "Xếp theo MAE CV trong cùng phiên bản, cấu hình và mô hình."}, combined=True)
    evaluation.sort(key=lambda row: (row[0], row[6], row[1], row[2], row[3]))
    sheet("Evaluation", ["Nhóm giờ chấm", "Phiên bản", "Cấu hình", "Mô hình", "Giờ train", "Giờ chấm",
                         "MAE", "RMSE", "R²", "Giảm MAE", "Mã lần chạy",
                         "Giờ chấm từ (CST)", "Giờ chấm đến (CST)", "Địa điểm đo"],
          evaluation, [23, 13, 24, 26, 13, 13, 14, 14, 12, 15, 38, 24, 24, 70],
          {**metric_notes,
           "Nhóm giờ chấm": "Chỉ so trực tiếp trong cùng nhóm. Kiểm tra thêm cột Giờ train khi giải thích chênh lệch.",
           "Giờ chấm từ (CST)": "Mốc đầu của các quan sát validation theo CST như mô tả của UCI.",
           "Mã lần chạy": "Thời điểm trong mã dùng giờ Việt Nam (UTC+7)."},
          combined=True)
    book.active = 0
    for label in ("Đối chứng A-B", "Đối chứng B-C"):
        tab = _sheet_name(version, label)
        if tab in book.sheetnames and tab not in written:
            book.remove(book[tab])

    output_dir.mkdir(parents=True, exist_ok=True)
    _save_workbook(book, path)
    return path


def load_experiment_workbook(version, output_dir, data_path, *, path=None):
    """Đọc lại dự đoán và tham số, xác nhận cùng bản CSV đầu vào."""
    import pandas as pd
    from openpyxl import load_workbook

    if not re.fullmatch(r"V_[1-4]", version):
        raise ValueError(f"Phiên bản workbook không hợp lệ: {version}")
    path = Path(output_dir) / WORKBOOK_NAME if path is None else Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Chưa có {path}. Hãy chạy {version} trước.")
    digest = hashlib.sha256(Path(data_path).read_bytes()).hexdigest()
    with path.open("rb") as stream:
        book = load_workbook(stream, read_only=True, data_only=True)
        try:
            guide = _check_provenance(book, version, digest)
            prediction_rows = iter(book[_sheet_name(version, "Dự đoán")].values)
            headers = [header for header in next(prediction_rows) if header is not None]
            predictions = pd.DataFrame((row[:len(headers)] for row in prediction_rows if row[0] is not None),
                                       columns=headers)
            predictions["date_time"] = pd.to_datetime(predictions["date_time"], errors="raise")
            predictions.attrs["run_id"] = guide["Mã lần chạy"]
            predictions.attrs["prior_run"] = guide.get("Mã chạy đối chứng")
            result_rows = iter(book[_sheet_name(version, "Validation")].values)
            headers = next(result_rows)
            parameters = {}
            for values in result_rows:
                if values[0] is None:
                    continue
                row = dict(zip(headers, values))
                if row["Tham số đã chọn"] is not None:
                    parameters[f"{row['Cấu hình']}|{row['Mô hình']}"] = json.loads(row["Tham số đã chọn"])
        finally:
            book.close()
    return path, predictions, parameters


def validate_prediction_rows(predictions, target):
    """Chặn phép đối chứng nếu khác giờ, thứ tự hoặc lưu lượng thật."""
    import pandas as pd

    actual = predictions[["date_time", "traffic_volume"]].reset_index(drop=True)
    expected = target[["date_time", "traffic_volume"]].reset_index(drop=True)
    pd.testing.assert_frame_equal(actual, expected, check_dtype=False, check_exact=True)
