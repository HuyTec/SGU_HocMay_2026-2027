"""Demo Time + Weather: nhập ngày giờ và thời tiết, trả lưu lượng dự đoán.

Chạy từ thư mục metro_interstate_traffic_volume:
    streamlit run app/demo_time_weather.py

Mô hình là XGBoost cấu hình B với tham số đã chọn trong
notebooks/experiments/V_3.ipynb, fit trên tập train. Validation và test
không được dùng để fit. Cần chạy baseline_V_2 và baseline_V_3 trước để có
outputs/metrics/V_3_best_params.json.
"""

from datetime import date, datetime, time
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.data import federal_holidays, load_splits  # noqa: E402
from src.evaluation import regression_metrics  # noqa: E402
from src.features import (  # noqa: E402
    CONFIG_B, WEATHER_GROUPS, add_time_features, add_weather_features, build_features,
)
from src.models import load_best_params, make_model  # noqa: E402

WEATHER_NAMES = {
    "clear": "Trời quang", "clouds": "Nhiều mây", "drizzle": "Mưa phùn",
    "fog": "Sương mù dày", "haze": "Mù khô", "mist": "Sương mù nhẹ",
    "rain": "Mưa", "smoke": "Khói", "snow": "Tuyết", "squall": "Gió giật",
    "thunderstorm": "Giông",
}
DAY_NAMES = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]


@st.cache_resource(show_spinner="Đang huấn luyện mô hình trên tập train…")
def load_model():
    """Fit XGBoost cấu hình B trên train; trả mô hình, MAE validation và bảng thứ–giờ."""
    features = build_features(load_splits())
    train, validation = features["train"], features["validation"]
    params = load_best_params("V_3", PROJECT_DIR / "outputs")["B_thoi_tiet|XGBoost"]
    model = make_model("XGBoost", CONFIG_B).set_params(**params)
    model.fit(train[CONFIG_B], train["traffic_volume"])
    metrics = regression_metrics(validation["traffic_volume"], model.predict(validation[CONFIG_B]))
    profile = train.groupby(["day_of_week", "hour"])["traffic_volume"].mean()
    return model, metrics, profile


def make_rows(day: date, hours, weather: dict, is_holiday: bool) -> pd.DataFrame:
    """Tạo bảng đầu vào cùng định dạng với dữ liệu sau tiền xử lý."""
    frame = pd.DataFrame({
        "date_time": [datetime.combine(day, time(hour)) for hour in hours],
        "temp": weather["temp_c"] + 273.15,
        "rain_1h": weather["rain_1h"],
        "snow_1h": weather["snow_1h"],
        "clouds_all": weather["clouds_all"],
        "weather_main": " | ".join(sorted(weather["groups"])),
        "is_holiday": int(is_holiday),
    })
    frame["date_time"] = pd.to_datetime(frame["date_time"])
    return add_weather_features(add_time_features(frame))


st.set_page_config(page_title="Dự đoán lưu lượng giao thông", layout="wide")
st.title("Dự đoán lưu lượng giao thông theo giờ")
st.caption("I-94 hướng Tây, trạm ATR 301 (Minneapolis–St Paul). Cấu hình Time + Weather, không dùng lịch sử lưu lượng.")

try:
    model, validation_metrics, weekday_hour_profile = load_model()
except FileNotFoundError as error:
    st.error(f"{error}\n\nHãy chạy V_2.ipynb và V_3.ipynb trước.")
    st.stop()

with st.sidebar:
    st.header("Thời gian")
    day = st.date_input("Ngày", value=date(2017, 11, 7), format="DD/MM/YYYY")
    hour = st.slider("Giờ", 0, 23, 8)
    calendar = federal_holidays(pd.Timestamp(day), pd.Timestamp(day))
    holiday_name = calendar.iloc[0] if len(calendar) else None
    is_holiday = st.checkbox(
        "Ngày lễ", value=holiday_name is not None,
        help="Tự đánh dấu theo lịch lễ liên bang Mỹ; có thể chỉnh tay cho các sự kiện như State Fair.",
    )
    if holiday_name:
        st.caption(f"Lịch liên bang: {holiday_name}")

    st.header("Thời tiết")
    groups = st.multiselect(
        "Loại thời tiết", WEATHER_GROUPS, default=["clouds"],
        format_func=lambda name: f"{WEATHER_NAMES[name]} ({name})",
    )
    temp_c = st.slider("Nhiệt độ (°C)", -30.0, 37.0, 5.0, 0.5)
    rain_1h = st.number_input("Lượng mưa trong giờ (mm)", 0.0, 60.0, 0.0, 0.5)
    snow_1h = st.number_input("Lượng tuyết trong giờ (mm)", 0.0, 1.0, 0.0, 0.05)
    clouds_all = st.slider("Mây che phủ (%)", 0, 100, 75)

if not groups:
    st.warning("Chọn ít nhất một loại thời tiết.")
    st.stop()

weather = {"temp_c": temp_c, "rain_1h": rain_1h, "snow_1h": snow_1h,
           "clouds_all": clouds_all, "groups": groups}
day_rows = make_rows(day, range(24), weather, is_holiday)
prediction = np.clip(model.predict(day_rows[CONFIG_B]), 0, None)
reference = weekday_hour_profile.xs(day.weekday(), level="day_of_week").reindex(range(24)).to_numpy()

left, middle, right = st.columns(3)
left.metric(f"Dự đoán {hour:02d}:00", f"{prediction[hour]:,.0f} xe/giờ".replace(",", "."))
middle.metric(
    "Trung bình cùng thứ–giờ (train)", f"{reference[hour]:,.0f} xe/giờ".replace(",", "."),
)
right.metric("MAE trên validation", f"{validation_metrics['MAE']:,.0f} xe/giờ".replace(",", "."))

st.subheader(f"Cả ngày {DAY_NAMES[day.weekday()]}, {day:%d/%m/%Y}, giữ nguyên thời tiết đã nhập")
chart = pd.DataFrame(
    {"Dự đoán Time + Weather": prediction, "Trung bình cùng thứ–giờ (train)": reference},
    index=pd.Index(range(24), name="Giờ"),
)
st.line_chart(chart, x_label="Giờ trong ngày", y_label="Xe/giờ", color=["#eb6834", "#2a78d6"])

with st.expander("Bảng số liệu"):
    st.dataframe(chart.round(0).astype(int), width="stretch")

st.info(
    "Mức sai số tuyệt đối trung bình trên validation khoảng "
    f"{validation_metrics['MAE']:.0f} xe/giờ. Theo V_3.ipynb, thời tiết chỉ giảm MAE khoảng 1% so với "
    "chỉ dùng thời gian và ngày lễ; mô hình sai nhiều hơn vào ngày lễ, ngày sát lễ và ngày tuyết. "
    "Kết quả là dự đoán của mô hình, không phải quan hệ nhân quả."
)
