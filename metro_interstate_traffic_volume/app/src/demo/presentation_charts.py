"""Plotly figures for teaching; all values are supplied by verified services."""

from html import escape
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BLUE, ORANGE, RED, GRAY = '#2563eb', '#d97706', '#dc2626', '#64748b'


def controls(figure, labels):
    """Browser-side frames with play/pause/manual selection, no server timer."""
    figure.update_layout(updatemenus=[dict(type='buttons', x=0, y=-.13, direction='right',
        buttons=[dict(label='Phát từng bước', method='animate', args=[None, {
            'frame': {'duration': 1000, 'redraw': True}, 'transition': {'duration': 300}, 'fromcurrent': True}]),
                 dict(label='Dừng', method='animate', args=[[None], {'mode': 'immediate',
                         'frame': {'duration': 0, 'redraw': False}, 'transition': {'duration': 0}}])])],
        sliders=[dict(y=-.3, active=0, steps=[dict(label=label, method='animate', args=[[str(i)],
            {'mode': 'immediate', 'frame': {'duration': 0, 'redraw': True}, 'transition': {'duration': 200}}])
            for i, label in enumerate(labels)])], margin=dict(b=115))
    return figure


def pipeline(labels, values=None, active=None, animated=False):
    """Rectangles encode ordered stages; values never come from a simulation."""
    values = values or [''] * len(labels)
    n = len(labels)
    text = [escape(str(label)) + ('<br><b>' + escape(str(value)) + '</b>' if str(value) else '')
            for label, value in zip(labels, values)]
    def trace(index):
        return go.Scatter(x=list(range(n)), y=[0] * n, mode='markers+text', text=text,
                          textposition='middle center', textfont=dict(size=12, color='white'),
                          marker=dict(symbol='square', size=108, color=[BLUE if i <= index else GRAY for i in range(n)],
                                      line=dict(width=3, color=[BLUE if i <= index else GRAY for i in range(n)])),
                          hoverinfo='text')
    figure = go.Figure(trace(n - 1 if active is None else active))
    for i in range(n - 1):
        figure.add_annotation(x=i + .5, y=0, text='→', showarrow=False, font=dict(size=22, color=GRAY))
    figure.update_layout(height=255 if animated else 170, showlegend=False,
                         xaxis=dict(visible=False, range=[-.65, n - .35], fixedrange=True),
                         yaxis=dict(visible=False, range=[-1, 1], fixedrange=True),
                         margin=dict(l=4, r=4, t=10, b=10))
    if animated:
        figure.frames = [go.Frame(name=str(i), data=[trace(i)], traces=[0]) for i in range(n)]
        controls(figure, labels)
    return figure


def table_html(frame, selected_columns=(), tone=BLUE, caption=''):
    """Escaped HTML cells guarantee visible rectangular borders in Streamlit."""
    head = ''.join('<th>' + escape(str(c)) + '</th>' for c in frame.columns)
    rows = []
    for _, row in frame.iterrows():
        cells = []
        for col, value in row.items():
            style = f'border:3px solid {tone};font-weight:650' if col in selected_columns else 'border:1px solid #94a3b8'
            shown = 'Thiếu (NaN)' if pd.isna(value) else str(value)
            cells.append(f'<td style="{style};padding:9px">{escape(shown)}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return ('<div style="overflow-x:auto;margin:12px 0"><table style="border-collapse:collapse;width:100%;font-size:14px">'
            '<caption style="text-align:left;padding:6px">' + escape(caption) + '</caption>'
            '<thead><tr>' + head + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')


def before_after(before, after, labels=('Trước xử lý', 'Sau xử lý')):
    """Reveal actual row/column summaries rather than decorative motion."""
    columns = [c for c in before.columns if c in after.columns][:5]
    def values(frame):
        return [escape(str(c)) + '<br>' + escape('Thiếu' if pd.isna(frame[c].iloc[0]) else str(frame[c].iloc[0]))
                for c in columns]
    def trace(frame, y, color):
        return go.Scatter(x=list(range(len(columns))), y=[y] * len(columns), mode='markers+text',
                          marker=dict(symbol='square', size=94, color=color, line=dict(width=3, color=color)),
                          text=values(frame), textfont=dict(color='white', size=11), hoverinfo='text')
    figure = go.Figure([trace(before, 1, ORANGE), go.Scatter(x=[], y=[], mode='markers+text')])
    figure.frames = [go.Frame(name='0', data=[trace(before, 1, ORANGE), go.Scatter(x=[], y=[])], traces=[0, 1]),
                     go.Frame(name='1', data=[trace(before, 1, ORANGE), trace(after, 0, BLUE)], traces=[0, 1])]
    figure.update_layout(height=340, showlegend=False, xaxis=dict(visible=False, range=[-.65, len(columns)-.35]),
                         yaxis=dict(tickvals=[0, 1], ticktext=[labels[1], labels[0]], range=[-.6, 1.6]),
                         margin=dict(t=15, l=90, r=10, b=110))
    return controls(figure, list(labels))


def history_timeline(cells):
    """Seven rows of hourly cells plus t; missing selected cells are red."""
    data = cells.copy()
    positions = np.arange(len(data))
    colors = np.where(data.is_used, BLUE,
                      np.where(data.in_window, RED, np.where(data.is_current, ORANGE, GRAY)))
    figure = go.Figure(go.Scatter(x=positions % 24, y=-(positions // 24), mode='markers+text',
        text=data.date_time.dt.strftime('%H'), textfont=dict(size=10, color='white'),
        marker=dict(symbol='square', size=27, color=colors, line=dict(width=2, color=colors)),
        customdata=np.column_stack([data.date_time.astype(str), data.traffic_volume.fillna('Thiếu'), data.label]),
        hovertemplate='%{customdata[0]}<br>Số xe: %{customdata[1]}<br>%{customdata[2]}<extra></extra>'))
    for i in np.flatnonzero(data.in_window | data.is_current):
        figure.add_shape(type='rect', x0=i % 24-.46, x1=i % 24+.46, y0=-(i//24)-.46, y1=-(i//24)+.46,
                         line=dict(color=colors[i], width=3))
    figure.update_layout(height=390, showlegend=False, xaxis=dict(title='Giờ trong từng hàng (đọc trái → phải)',
        tickvals=[], range=[-1, 24], fixedrange=True), yaxis=dict(visible=False, range=[-7.7, .7], fixedrange=True),
        margin=dict(l=5, r=5, t=10, b=40))
    return figure


def prediction_animation(result):
    return pipeline(['C30', 'Ensemble', 'Dự đoán', 'Thực tế', 'Sai số'],
                    ['30 biến', '25 / 25 / 50', f"{result['prediction']:.2f}",
                     f"{result['actual']:.2f}", f"{result['absolute_error']:.2f}"], active=0, animated=True)


def calculation_animation(trace):
    """Hide unrevealed values, especially actual, until the appropriate frame."""
    from .calculation import STEPS
    values = [str(trace['at']), '30 biến float32', 'Đủ đầu vào', '3 predict thật',
              f"{trace['prediction']:.2f} xe/giờ", f"Actual {trace['actual']:.0f}; lỗi {trace['absolute_error']:.2f}"]
    figure = pipeline(STEPS, active=0, animated=True)
    def text(index):
        return [escape(label)+'<br>'+escape(values[i] if i <= index else 'Chưa mở') for i,label in enumerate(STEPS)]
    figure.data[0].text = text(0)
    for i, frame in enumerate(figure.frames):
        frame.data[0].text = text(i)
    return figure


def linked_errors(saved, at):
    """One timestamp drives both panels; NaN grid prevents joining missing hours."""
    rows = saved.set_index('date_time').sort_index()
    rows = rows.reindex(pd.date_range(rows.index.min(), rows.index.max(), freq='h'))
    figure = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=.10,
                           subplot_titles=('Thực tế và dự đoán · xe/giờ', 'Sai số tuyệt đối · xe/giờ'))
    for col, label, color in [('actual', 'Thực tế', GRAY), ('prediction', 'Dự đoán', BLUE)]:
        figure.add_trace(go.Scatter(x=rows.index, y=rows[col], name=label, line=dict(color=color, width=1.5),
                                   connectgaps=False), row=1, col=1)
    error = (rows.prediction - rows.actual).abs()
    figure.add_trace(go.Scatter(x=rows.index, y=error, name='Sai số tuyệt đối',
                               line=dict(color=ORANGE), connectgaps=False), row=2, col=1)
    at = pd.Timestamp(at)
    if at in rows.index:
        chosen = rows.loc[at]
        for row, value in [(1, chosen.prediction), (2, error.loc[at])]:
            figure.add_trace(go.Scatter(x=[at], y=[value], mode='markers', name='Giờ đang xem',
                marker=dict(size=12, color=RED, symbol='square-open', line=dict(width=3)), showlegend=row == 1), row=row, col=1)
            figure.add_vrect(x0=at-pd.Timedelta(minutes=30), x1=at+pd.Timedelta(minutes=30),
                             line_width=2, line_color=RED, fillcolor=RED, opacity=.12, row=row, col=1)
    figure.update_layout(height=550, hovermode='x unified', margin=dict(l=10, r=10, t=45, b=30),
                         legend=dict(orientation='h', y=1.12), uirevision='saved-test')
    return figure
