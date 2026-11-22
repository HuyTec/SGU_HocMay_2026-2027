"""Descriptive charts; no feature engineering, fitting or model prediction."""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.figure import Figure


def lines_with_gaps(frame, y_title='Xe/giờ', height=300):
    """Use explicit segments to avoid connecting any missing hourly records."""
    rows = []
    for name in frame:
        values = frame[name]
        segment = values.isna().cumsum()
        for at, value in values.items():
            if pd.notna(value):
                rows.append({'Giờ': at, 'Giá trị': float(value), 'Chuỗi': name, 'Đoạn': f'{name}-{segment.loc[at]}'})
    if not rows:
        st.info('Khoảng này chưa có giá trị để vẽ.')
        return
    chart = alt.Chart(pd.DataFrame(rows)).mark_line(point=True).encode(
        x='Giờ:T', y=alt.Y('Giá trị:Q', title=y_title), color='Chuỗi:N', strokeDash='Chuỗi:N',
        detail='Đoạn:N', tooltip=['Giờ:T', 'Chuỗi:N', 'Giá trị:Q']).properties(height=height)
    st.altair_chart(chart, width='stretch')


def coverage_figure(comparison):
    """Build a standalone monthly coverage figure and its exact count table."""
    coverage_data = comparison['daily_coverage'].rename(columns={'Ngày': 'day', 'Nhóm': 'group', 'Số giờ': 'hours'})
    coverage_data = coverage_data.assign(month=coverage_data.day.dt.strftime('%Y-%m')).groupby(
        ['month', 'group'], as_index=False).hours.sum()
    pivot = coverage_data.pivot(index='month', columns='group', values='hours').fillna(0)
    # A standalone figure avoids the blank stacked-bar render observed in the browser.
    figure = Figure(figsize=(12, 4.8), layout='constrained')
    axis = figure.subplots()
    positions = np.arange(len(pivot))
    bottom = np.zeros(len(pivot))
    colors = ['#2563eb', '#d97706', '#0f766e', '#64748b', '#be185d']
    for color, group in zip(colors, pivot.columns):
        values = pivot[group].to_numpy(dtype=float)
        axis.bar(positions, values, bottom=bottom, label=group, color=color, width=.72)
        bottom += values
    axis.set_xticks(positions, pivot.index, rotation=30, ha='right')
    axis.set_ylabel('Số giờ lịch trong tháng')
    axis.set_xlabel('Tháng · phạm vi dữ liệu hiện có')
    axis.set_ylim(0, max(bottom) * 1.08)
    axis.legend(loc='upper left', bbox_to_anchor=(0, -.25), ncol=2, frameon=False, fontsize=9)
    axis.spines[['top', 'right']].set_visible(False)
    axis.grid(axis='y', alpha=.2)
    axis.set_axisbelow(True)
    return figure, pivot


def source_charts(comparison):
    """Show exact overlap separately from differences between disjoint periods."""
    overlap = comparison['overlap']
    st.subheader('Độ giao nhau của hai bộ dữ liệu · không trùng toàn bộ')
    st.dataframe(comparison['membership'], hide_index=True, width='stretch')
    st.caption(f"Mẫu số tỷ lệ: toàn bộ {comparison['n_mndot']:,} bản ghi giờ MnDOT 2018 của trạm/hướng đã chọn. "
               'Giao timestamp và khớp giá trị là hai kiểm tra khác nhau.')
    figure, pivot = coverage_figure(comparison)
    st.pyplot(figure, width='stretch')
    with st.expander('Số giờ theo tháng và nhóm · dữ liệu của biểu đồ'):
        st.dataframe(pivot.astype(int), width='stretch')
    st.caption('Mỗi cột tổng hợp số giờ lịch trong tháng, theo phạm vi file đang có (tháng 12 chỉ đến ngày 11). '
               'Phần vắng cả hai nguồn giữ nhãn riêng; không biến thành lưu lượng 0. '
               f"Ranh giới giai đoạn: sau giờ cuối UCI {comparison['uci_end']}.")
    matched = int(overlap.difference.eq(0).sum())
    st.write(f'Riêng {len(overlap):,} giờ giao timestamp: {matched:,} giờ khớp lưu lượng. '
             'Không có nghĩa toàn bộ bộ MnDOT trùng UCI; không phải sai số mô hình.')
    st.subheader('Lưu lượng hai nguồn · gồm phần giao và phần không giao')
    st.caption('Mặc định xem qua ranh giới cuối UCI: đường UCI dừng, MnDOT tiếp tục. '
               'Chỉ các giờ chung mới có thể nằm chồng lên nhau.')
    chosen = st.date_input('Ngày bắt đầu đối chiếu hai nguồn',
                           value=(comparison['uci_end'].normalize() - pd.Timedelta(days=2)).date(),
                           min_value=comparison['traffic_grid'].index.min().date(),
                           max_value=comparison['traffic_grid'].index.max().date(), key='overlap_day')
    begin = pd.Timestamp(chosen)
    end = min(comparison['traffic_grid'].index.max(), begin + pd.Timedelta(hours=167))
    # Outer join retains hours measured by only one source; they are not paired differences.
    grid = comparison['traffic_grid'].reindex(pd.date_range(begin, end, freq='h', name='date_time'))
    lines_with_gaps(grid)
    delta = (grid.MnDOT - grid.UCI).rename('MnDOT − UCI').to_frame()
    lines_with_gaps(delta, 'Chênh lệch xe/giờ', height=150)
    st.caption(f'Cửa sổ {begin} → {end}. Chênh lệch chỉ tính khi cả hai nguồn có target; thiếu một phía giữ khoảng trống.')
    st.subheader('Dữ liệu mới so với cũ · hai giai đoạn riêng')
    st.dataframe(comparison['summary'], hide_index=True, width='stretch')
    histogram = alt.Chart(comparison['histogram']).mark_line(point=True).encode(
        x=alt.X('Từ xe/giờ:Q', title='Lưu lượng · các bin dùng chung'), y='Tỷ lệ (%):Q',
        color='Nguồn:N', strokeDash='Nguồn:N', tooltip=['Nguồn:N', 'Từ xe/giờ:Q', 'Đến xe/giờ:Q', 'Số mẫu:Q', 'Tỷ lệ (%):Q'])
    st.altair_chart(histogram.properties(height=260), width='stretch')
    weekday = st.selectbox('Thứ để đối chiếu mẫu theo giờ', range(7),
                           format_func=lambda value: ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ nhật'][value],
                           key='compare_weekday')
    profile = comparison['profile'].loc[comparison['profile'].weekday.eq(weekday)]
    profile = profile.rename(columns={'source': 'Nguồn', 'hour': 'Giờ', 'mean': 'Lưu lượng trung bình', 'count': 'Số mẫu'})
    chart = alt.Chart(profile).mark_line(point=True).encode(x='Giờ:O', y='Lưu lượng trung bình:Q',
        color='Nguồn:N', strokeDash='Nguồn:N', tooltip=['Nguồn:N', 'Giờ:O', 'Lưu lượng trung bình:Q', 'Số mẫu:Q'])
    st.altair_chart(chart.properties(height=260), width='stretch')
    st.caption('Cũ: UCI trong năm 2018 đến hết tháng 9. Mới: MnDOT sau UCI, tháng 10–12. '
               'Khác mùa, độ phủ và số mẫu; biểu đồ mô tả thay đổi phân phối, chưa chứng minh drift mô hình hoặc nguyên nhân.')


def error_charts(predictions, label):
    """Visualize residuals from supplied predictions; never call an estimator."""
    valid = predictions.loc[np.isfinite(predictions.prediction) & np.isfinite(predictions.actual) & predictions.actual.ge(0)].copy()
    st.subheader(f'Biểu đồ sai số · {label}')
    if valid.empty:
        st.info('Chưa có giờ có cả prediction và actual hợp lệ để vẽ sai số.')
        return
    valid['residual'] = valid.prediction - valid.actual
    valid['absolute_error'] = valid.residual.abs()
    st.caption(f'n = {len(valid):,} giờ · residual = prediction − actual. Dương: dự đoán cao; âm: dự đoán thấp.')
    counts, edges = np.histogram(valid.residual, bins=40)
    histogram = pd.DataFrame({'Từ': edges[:-1], 'Đến': edges[1:], 'Số giờ': counts})
    chart = alt.Chart(histogram).mark_bar(orient='vertical').encode(x=alt.X('Từ:Q', title='Sai số có dấu · xe/giờ'), x2='Đến:Q',
                                               y='Số giờ:Q', tooltip=['Từ:Q', 'Đến:Q', 'Số giờ:Q'])
    zero = alt.Chart(pd.DataFrame({'zero': [0]})).mark_rule(color='#c2410c', strokeDash=[4, 4]).encode(x='zero:Q')
    st.altair_chart((chart + zero).properties(height=260), width='stretch')
    by_day = valid.set_index('date_time').absolute_error.resample('D').agg(['mean', 'count']).reset_index()
    # Mean becomes null on absent days, and segments keep the visual gap.
    by_day['segment'] = by_day['mean'].isna().cumsum().astype(str)
    daily = alt.Chart(by_day).mark_line(point=True).encode(x=alt.X('date_time:T', title='Ngày'),
        y=alt.Y('mean:Q', title='MAE trong ngày · xe/giờ'), detail='segment:N',
        tooltip=['date_time:T', alt.Tooltip('mean:Q', title='MAE'), alt.Tooltip('count:Q', title='Số giờ được chấm')])
    st.altair_chart(daily.properties(height=230), width='stretch')
    by_hour = valid.assign(hour=valid.date_time.dt.hour).groupby('hour').absolute_error.agg(['mean', 'count']).reset_index()
    hourly = alt.Chart(by_hour).mark_bar().encode(x=alt.X('hour:O', title='Giờ trong ngày'),
        y=alt.Y('mean:Q', title='MAE theo giờ · xe/giờ'), tooltip=['hour:O', 'mean:Q', alt.Tooltip('count:Q', title='Số mẫu')])
    st.altair_chart(hourly.properties(height=230), width='stretch')
    st.caption('Mỗi nhóm có mẫu số riêng trong tooltip. Biểu đồ chỉ mô tả sai số đã có, không xác định nguyên nhân.')
