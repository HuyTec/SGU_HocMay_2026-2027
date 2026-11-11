"""Ghi kết quả 5-fold CV của House Prices vào nhật ký Excel."""

from datetime import datetime, timedelta, timezone
from math import isfinite
from pathlib import Path
from statistics import mean, stdev
from tempfile import NamedTemporaryFile

from openpyxl import Workbook, load_workbook
from openpyxl.utils.cell import range_boundaries
from openpyxl.worksheet.table import Table, TableStyleInfo


VIETNAM_TIME = timezone(timedelta(hours=7))
LOG_PATH = Path(__file__).with_name("experiment_log.xlsx")
HEADERS = (
    "Mã lần chạy", "Ngày giờ chạy", "Mô hình", "Tham số mô hình",
    "Thiết lập CV", "RMSE TB", "Độ lệch chuẩn", "Fold 1", "Fold 2",
    "Fold 3", "Fold 4", "Fold 5", "Nguồn",
)


def _get_log_sheet(workbook):
    if "Experiment_Log" in workbook.sheetnames:
        return workbook["Experiment_Log"]

    sheet = workbook.active
    if len(workbook.worksheets) == 1 and sheet.max_row == 1 and sheet.max_column == 1 and sheet["A1"].value is None:
        sheet.title = "Experiment_Log"
    else:
        sheet = workbook.create_sheet("Experiment_Log")
    sheet["A2"] = "Nhật ký thử nghiệm House Prices"
    sheet["A3"] = "5-fold CV trên train • RMSE trên ln(SalePrice)"
    sheet["A4"] = "Ngày giờ chạy theo giờ Việt Nam."
    for col, header in enumerate(HEADERS, start=1):
        sheet.cell(row=6, column=col, value=header)
    for col, width in {"A": 16, "B": 24, "C": 22, "D": 30, "E": 38, "F": 14,
                       "G": 18, "H": 11, "I": 11, "J": 11, "K": 11, "L": 11, "M": 42}.items():
        sheet.column_dimensions[col].width = width
    sheet.freeze_panes = "A7"
    return sheet


def append_experiment(*, started_at: datetime, model: str, parameters: str,
                      cv_setup: str, fold_scores, source: str,
                      log_path: Path = LOG_PATH) -> str:
    """Thêm một kết quả đã tính và trả mã lần chạy."""
    scores = tuple(float(score) for score in fold_scores)
    if len(scores) != 5 or any(not isfinite(score) or score < 0 for score in scores):
        raise ValueError("Cần đúng 5 điểm RMSE hữu hạn và không âm.")
    if started_at.utcoffset() is None:
        raise ValueError("Ngày giờ chạy phải có múi giờ.")

    path = Path(log_path)
    workbook = load_workbook(path) if path.exists() else Workbook()
    try:
        sheet = _get_log_sheet(workbook)
        if tuple(cell.value for cell in sheet[6][:len(HEADERS)]) != HEADERS:
            raise ValueError("Tiêu đề trong Experiment_Log khác cấu trúc nhật ký dự kiến.")

        table = sheet.tables.get("HousePricesRuns")
        last_row = range_boundaries(table.ref)[3] if table else sheet.max_row
        row = last_row + 1
        if any(sheet.cell(row, col).value is not None for col in range(1, 14)):
            raise ValueError("Dòng kế tiếp trong nhật ký đã có dữ liệu.")

        ids = [sheet.cell(i, 1).value for i in range(7, last_row + 1)]
        used_numbers = [int(x[3:]) for x in ids
                        if isinstance(x, str) and x.startswith("HP-") and x[3:].isdigit()]
        run_id = f"HP-{max(used_numbers, default=0) + 1:03d}"
        local_time = started_at.astimezone(VIETNAM_TIME).replace(tzinfo=None)
        values = (run_id, local_time, model, parameters, cv_setup,
                  mean(scores), stdev(scores), *scores, source)
        for col, value in enumerate(values, 1):
            sheet.cell(row, col, value)
        sheet.cell(row, 2).number_format = "dd/mm/yyyy hh:mm:ss"
        for col in range(6, 13):
            sheet.cell(row, col).number_format = "0.00000"

        table_range = f"A6:M{row}"
        if table is None:
            table = Table(displayName="HousePricesRuns", ref=table_range)
            table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
            sheet.add_table(table)
        else:
            table.ref = table_range
            if table.autoFilter is not None:
                table.autoFilter.ref = table_range

        # Ghi vào file tạm rồi thay thế để bản gốc còn nguyên nếu lưu thất bại.
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(dir=path.parent, suffix=".xlsx", delete=False) as temp:
            temp_path = Path(temp.name)
        try:
            workbook.save(temp_path)
            temp_path.replace(path)
        except PermissionError as exc:
            raise PermissionError(f"Không ghi được {path.name}. Hãy đóng file Excel rồi chạy lại.") from exc
        finally:
            temp_path.unlink(missing_ok=True)
        return run_id
    finally:
        workbook.close()
