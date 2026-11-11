"""Lưu kết quả một phiên bản thí nghiệm vào một workbook Excel riêng."""

from datetime import datetime
from pathlib import Path
import json
import re

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill


def _cell(value):
    """Chuyển dữ liệu lồng nhau hoặc kiểu numpy về giá trị Excel đọc được."""
    if hasattr(value, "item") and callable(value.item):
        try:
            value = value.item()
        except ValueError:
            pass
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False, default=str)
    elif value is not None and not isinstance(value, (str, int, float, bool, datetime)):
        value = str(value)
    # Không để dữ liệu đầu vào vô tình trở thành công thức Excel.
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        value = "'" + value
    return value


def _rows(data):
    """Nhận dict, danh sách dict hoặc pandas DataFrame (không bắt buộc pandas)."""
    if data is None:
        return []
    if hasattr(data, "to_dict"):
        data = data.to_dict(orient="records")
    if isinstance(data, dict):
        return [{"Nội dung": key, "Giá trị": value} for key, value in data.items()]
    if isinstance(data, (list, tuple)) and all(isinstance(row, dict) for row in data):
        return list(data)
    raise TypeError("Dữ liệu phải là dict, danh sách dict hoặc pandas DataFrame.")


def _write_sheet(sheet, data):
    rows = _rows(data)
    if not rows:
        sheet.append(["Chưa cung cấp dữ liệu"])
        sheet.column_dimensions["A"].width = 35
        return
    columns = list(dict.fromkeys(key for row in rows for key in row))
    sheet.append([str(key) for key in columns])
    for row in rows:
        sheet.append([_cell(row.get(key)) for key in columns])
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="245574")
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for column in sheet.columns:
        letter = column[0].column_letter
        sheet.column_dimensions[letter].width = min(65, max(16, max(len(str(c.value or "")) for c in column) + 2))
        for cell in column:
            cell.alignment = Alignment(vertical="top", wrap_text=True)


def save_experiment(name, description, version, *, dataset=None, validation=None,
                    hyperparameters=None, tuning_cv=None, output_dir=None):
    """Lưu một lần chạy; trả về đường dẫn workbook, không ghi đè lần chạy khác.

    Các mục dataset, validation, hyperparameters và tuning_cv nhận dict,
    list[dict] hoặc DataFrame. Thời gian lấy theo múi giờ của máy đang chạy.
    """
    for label, value in (("name", name), ("description", description), ("version", version)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} phải là chuỗi không rỗng")
    now = datetime.now().astimezone()
    base = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent
    base.mkdir(parents=True, exist_ok=True)
    safe = lambda s: re.sub(r"[^\w.-]+", "_", s.strip(), flags=re.UNICODE).strip("._") or "experiment"
    stem = f"{now:%Y-%m-%d_%H-%M-%S}_{safe(version)}_{safe(name)}"
    overview = {"Tên thí nghiệm": name, "Phiên bản": version, "Mô tả": description,
                "Thời gian lưu": now.isoformat(timespec="seconds")}
    overview.update({f"Dữ liệu: {k}": v for k, v in (dataset or {}).items()} if isinstance(dataset, dict) else {})
    book = Workbook()
    book.remove(book.active)
    for title, content in (("Tong quan", overview), ("Validation", validation),
                           ("Hyperparameters", hyperparameters), ("Tuning CV", tuning_cv)):
        _write_sheet(book.create_sheet(title), content)
    if dataset is not None and not isinstance(dataset, dict):
        raise TypeError("dataset phải là dict mô tả bộ dữ liệu.")
    # Chế độ x bảo đảm không ghi đè ngay cả khi hai lần lưu cùng giây.
    for index in range(10000):
        path = base / f"{stem}{'' if index == 0 else '_' + str(index)}.xlsx"
        try:
            with path.open("xb") as file:
                book.save(file)
            return path
        except FileExistsError:
            continue
    raise FileExistsError("Không tạo được tên file thí nghiệm duy nhất.")
