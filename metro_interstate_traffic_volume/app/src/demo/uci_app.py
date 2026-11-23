"""Six-tab UCI-first Streamlit presentation, with independent user-driven fragments."""
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from . import service as demo, weather as ow, charts
from . import presentation as view, presentation_charts as visual
from . import calculation


@st.cache_resource(show_spinner='Đang kiểm chứng mô hình cuối…')
def model(token):
    return demo.audited_bundle()


@st.cache_data(show_spinner=False)
def results(token):
    return view.verified_results()


@st.cache_data(show_spinner=False)
def uci(token):
    plan_path = demo.FINAL/'final_fit_plan.json'
    if plan_path.is_file() and demo.sha256(demo.UCI) != demo.json_file(plan_path)['data_sha256']:
        raise ValueError('Bảng UCI theo giờ khác phiên bản dùng fit C30; dừng tạo đầu vào inference.')
    return demo.load_uci_sources()


@st.cache_data(show_spinner=False)
def splits(token, _hourly):
    return view.split_summary(_hourly)


@st.cache_data(show_spinner=False)
def features(token, at, _hourly, _bundle):
    return view.inspected_features(_hourly, at, _bundle)


@st.cache_data(show_spinner=False)
def examples(token, kind, _raw, _hourly):
    return (view.duplicate_example(_raw, _hourly) if kind == 'duplicate'
            else view.cleaning_example(_raw, _hourly, kind))


@st.cache_data(show_spinner=False)
def external_sources(token):
    return demo.load_sources()


@st.cache_data(show_spinner=False)
def preview(token, policy, _context, _weather, end):
    return ow.attach_preview(_context, _weather, end, policy)


def plot(figure, key):
    st.plotly_chart(figure, width='stretch', key=key, config={'displaylogo': False, 'scrollZoom': False})


def metric_strip(values):
    for col, name in zip(st.columns(3), ['MAE', 'RMSE', 'R2']):
        value = values.get(name)
        col.metric('R²' if name == 'R2' else name,
                   'Chưa có' if value is None else f'{value:.4f}' if name == 'R2' else f'{value:,.2f} xe/giờ')


def feature_table(matrix, highlight=None):
    if highlight in matrix:
        selected = pd.DataFrame({'Đặc trưng đang xem': [highlight], 'Giá trị đưa vào C30': [matrix[highlight].iloc[0]]})
        st.html(visual.table_html(selected, selected.columns, caption='Ô xanh được đưa vào vector cuối'))
    st.dataframe(matrix.T.rename_axis('Đặc trưng').rename(columns={matrix.index[0]: 'Giá trị float32'}), width='stretch')


def move_step(delta=None):
    st.session_state['walk_step'] = 0 if delta is None else max(0, min(5, st.session_state.get('walk_step', 0) + delta))


@st.fragment
def walkthrough(raw, hourly, token, at, reduced):
    step = st.session_state.setdefault('walk_step', 0)
    st.subheader(f'Bước {step + 1}/6 · {view.STEPS[step]}')
    st.progress((step + 1) / len(view.STEPS))
    back, nxt, reset = st.columns(3)
    back.button('Quay lại', key='walk_back', on_click=move_step, args=(-1,), disabled=step == 0)
    nxt.button('Bước tiếp theo', key='walk_next', on_click=move_step, args=(1,), disabled=step == 5)
    reset.button('Đặt lại', key='walk_reset', on_click=move_step)
    st.caption('Viền xanh: được dùng · cam: cần chú ý · đỏ: không hợp lệ · xám: ngoài bước hiện tại. '
               'Animation có Phát/Dừng và chọn trạng thái; không tự chạy.')
    if raw is None or hourly is None:
        st.warning('Thiếu UCI để trình diễn xử lý; kết quả test đã lưu vẫn có thể xem ở tab 4/5.')
        return
    if step == 0:
        st.markdown('**Đầu vào:** CSV UCI gốc. **Thao tác:** đọc cấu trúc và giữ nhãn ngày lễ `None`. '
                    '**Đầu ra:** chưa đổi giá trị, chưa học thống kê.')
        st.html(visual.table_html(raw.head(8), ['date_time', 'traffic_volume'], caption='8 dòng thật đầu tiên'))
        with st.expander('Xem hoặc tải toàn bộ CSV gốc'):
            st.dataframe(raw, width='stretch')
            st.download_button('Tải CSV UCI gốc', demo.UCI_RAW.read_bytes(), demo.UCI_RAW.name, 'text/csv')
    elif step in (1, 2):
        before, after = examples(token, 'duplicate', raw, hourly)
        if step == 1:
            st.markdown('**Đầu vào:** các dòng cùng timestamp. **Kiểm tra:** target trong cùng giờ phải nhất quán. '
                        '**Vì sao:** nhiều nhãn weather không có nghĩa xe được đếm thêm lần nữa.')
            st.html(visual.table_html(before, ['date_time', 'traffic_volume'], visual.ORANGE, 'Cùng giờ · cần gộp'))
            st.caption(f'{len(before)} dòng ở cùng giờ, {before.traffic_volume.nunique()} giá trị target. '
                       f'Toàn CSV có {len(raw)-raw.date_time.nunique():,} dòng dư theo timestamp, không phải tất cả trùng hoàn toàn.')
        else:
            st.markdown('**Phép biến đổi thật:** giữ một target mỗi giờ, numeric weather lấy median các giá trị phân biệt, '
                        'nhãn chuẩn hóa chữ thường và gộp duy nhất. **Đầu ra:** một dòng cho giờ này.')
            left, right = st.columns(2)
            cols = ['date_time', 'traffic_volume', 'weather_main']
            with left:
                st.html(visual.table_html(before[cols], ['date_time'], visual.ORANGE, 'Trước · nhiều dòng'))
            with right:
                st.html(visual.table_html(after[cols], ['traffic_volume', 'weather_main'], caption='Sau · không cộng lặp target'))
            if not reduced:
                cols = ['traffic_volume', 'temp', 'rain_1h']
                plot(visual.before_after(before[cols], after[cols]), 'merge_animation')
        st.caption('Gọi build_hourly_target/build_hourly_weather của dự án và đối chiếu bảng chuẩn. '
                   'Median gộp cùng giờ khác với median điền thiếu học từ train; chưa fit thống kê trên test.')
    elif step == 3:
        case = st.radio('Ngoại lệ thật cần xem', ['temp', 'rain'], horizontal=True, key='clean_case',
                        format_func=lambda x: 'Nhiệt độ 0 K' if x == 'temp' else 'Mưa 9.831,3 mm')
        before, after = examples(token, case, raw, hourly)
        col = 'temp' if case == 'temp' else 'rain_1h'
        st.markdown('**Thao tác:** đánh dấu ngoại lệ thành thiếu (`NaN`), không xóa giờ hoặc tạo số xe giả. '
                    '**Đầu ra:** hourly_unfilled giữ ô thiếu, chưa điền bằng thống kê toàn tập.')
        left, right = st.columns(2)
        with left:
            st.html(visual.table_html(before[['date_time', col]], [col], visual.RED, 'Trước · không hợp lệ'))
        with right:
            st.html(visual.table_html(after[['date_time', col]], [col], visual.ORANGE, 'Sau · giữ thiếu'))
        if not reduced:
            plot(visual.before_after(before[[col]], after[[col]]), 'clean_animation')
        st.info('Khi tạo C30: nhiệt độ chỉ tra quan sát quá khứ tối đa 6 giờ, rồi median tháng–giờ/fallback đã học từ train tương ứng. '
                'Mưa dùng median đã lưu. Không học encoder/scaler/imputer trên test, không điền traffic/history.')
        st.caption(f'Sau làm sạch còn {int(hourly.temp.isna().sum())} nhiệt độ thiếu và '
                   f'{int(hourly.rain_1h.isna().sum())} lượng mưa thiếu để điền theo phạm vi train.')
    elif step == 4:
        row = hourly.loc[hourly.date_time.eq(at)]
        if row.empty:
            st.info('Giờ đang chọn không có trong bảng UCI.')
            return
        encoded = view.add_weather_features(view.add_time_features(row))
        st.markdown('**Thao tác thật:** K → °C; giờ/thứ/tháng → sin/cos; mỗi nhãn weather → một cờ. '
                    '**Đầu ra:** nhóm lịch/weather. Thêm ba history ở tab 3 để đủ 30 biến.')
        cols = ['hour', 'hour_sin', 'hour_cos', 'temp_c', 'weather_clouds', 'weather_rain', 'weather_snow']
        st.html(visual.table_html(encoded[cols], cols[1:], caption=f'Feature dẫn xuất tại {at}'))
        st.caption('12 biến lịch/ngày lễ + 4 weather số + 11 cờ weather + 3 history = 30. '
                   'Phép đổi cố định không học từ target; vector cuối lấy từ prepare_features chung.')
    else:
        summary = splits(token, hourly)
        st.markdown('**Thao tác:** sắp thời gian, chia 70/15/15 theo số giờ quan sát. '
                    '**Vì sao:** học quá khứ, đánh giá giai đoạn sau; không random split.')
        plot(visual.pipeline(['Train', 'Validation', 'Test'], [str(n)+' giờ' for n in summary['Số giờ quan sát']]), 'split_pipeline')
        st.html(visual.table_html(summary, ['Từ', 'Đến'], caption='Ranh giới thời gian · báo cả số giờ đủ history'))
        st.info('Expanding CV nằm trong train; imputer/scaler học trong từng fold-train. Validation để lựa chọn. '
                'Sau khi chốt, refit train + validation đủ history; test là khối đánh giá cuối.')


@st.fragment
def history_panel(hourly, at, bundle, token):
    st.subheader(f'Đầu vào tại {at}')
    if hourly is None:
        st.warning('Chưa có bảng UCI theo giờ để tra lịch sử.')
        return
    feature = st.radio('Thông tin quá khứ cần tô sáng', list(view.FEATURE_LABELS),
                       format_func=view.FEATURE_LABELS.get, horizontal=True, key='history_feature')
    cells = view.history_cells(hourly, at, feature)
    plot(visual.history_timeline(cells), 'history_timeline')
    st.caption('Mỗi ô = một giờ thật. Xanh: được dùng; đỏ: thiếu quan sát cần dùng; cam: t, target không tham gia history. '
               'Rê chuột xem timestamp và số xe. Đọc trái sang phải rồi xuống hàng.')
    history = demo.add_history_features(hourly).set_index('date_time')
    if at not in history.index:
        st.warning('Không có dòng UCI tại giờ này.')
        return
    row = history.loc[at]
    for col, name in zip(st.columns(3), view.FEATURE_LABELS):
        col.metric(view.FEATURE_LABELS[name], 'Thiếu' if pd.isna(row[name]) else f'{row[name]:,.2f} xe/giờ')
    if feature == 'mean_24h':
        st.latex(r'\mathrm{mean\_24h}(t)=\frac{1}{N}\sum_{s\in[t-24h,t),\;y_s\;\mathrm{available}} y_s,\quad N\ge18')
        st.write(f'Cửa sổ [{at-pd.Timedelta(hours=24)}, {at}) có {int(cells.is_used.sum())}/24 quan sát; không dùng giờ t.')
    else:
        st.write(f"{feature} lấy giá trị tại **{cells.loc[cells.in_window, 'date_time'].iloc[0]}**, không tra theo vị trí dòng.")
    with st.expander('Đúng những giờ tham gia feature'):
        st.dataframe(cells.loc[cells.in_window, ['date_time', 'traffic_volume', 'is_used', 'label']], hide_index=True)
    if bundle is None:
        st.info('Chưa có artifact hợp lệ để xác minh vector C30; history vẫn lấy từ pipeline gốc.')
        return
    try:
        st.subheader('Vector C30 thật đưa vào mô hình')
        feature_table(features(token, at, hourly, bundle), feature)
        st.caption('30 cột đúng thứ tự artifact, dtype float32. Weather cùng giờ là giả định sẵn có; '
                   'không dùng target tại t hoặc tương lai tạo history.')
    except ValueError as error:
        st.warning(str(error))


@st.fragment
def prediction_panel(hourly, saved, bundle, at, token, reduced):
    st.subheader('Một giờ, một kết quả có thể đối chiếu')
    if saved is None or saved.loc[saved.date_time.eq(at)].empty:
        st.info('Chọn một giờ thuộc test có kết quả đã lưu; không chấm train/validation như test.')
        return
    matrix = None
    if hourly is not None and bundle is not None:
        try:
            matrix = features(token, at, hourly, bundle)
        except ValueError:
            pass
    live_ready = matrix is not None and np.isfinite(matrix.to_numpy()).all()
    choices = ['Kết quả đã lưu (Stored Prediction)']
    if live_ready:
        choices.append('Mô hình chạy trực tiếp (Live Model Inference)')
        choices.append('Chạy và giải thích từng bước')
    if st.session_state.get('prediction_mode') not in choices:
        st.session_state.pop('prediction_mode', None)
    label = st.radio('Cách lấy kết quả', choices, key='prediction_mode')
    mode = 'trace' if label == 'Chạy và giải thích từng bước' else 'live' if label.startswith('Mô hình') else 'stored'
    st.caption('Stored chỉ đọc file test. Live gọi ba mô hình thật cho đúng một giờ và đối chiếu file lưu; '
               'không fit, không đổi tham số hoặc chấm lại toàn test.')
    if not live_ready:
        st.caption('Live chưa khả dụng: thiếu artifact hợp lệ hoặc đầu vào C30 của giờ này.')
    signature = (token, str(at), mode)
    if st.session_state.get('prediction_signature') != signature:
        st.session_state.pop('presentation_prediction', None)
        for key in ['calculation_trace', 'calculation_step', 'boosting_trace']:
            st.session_state.pop(key, None)
        st.session_state['prediction_signature'] = signature
    if matrix is not None:
        st.dataframe(matrix[['hour', 'temp_c', 'lag_24h', 'lag_168h', 'mean_24h']], width='stretch')
    if st.button('Xem kết quả dự đoán', key='show_prediction', type='primary'):
        try:
            if mode == 'trace':
                with st.spinner('Đang tính thật và ghi lại từng mô hình…'):
                    st.session_state['calculation_trace'] = calculation.run(hourly, at, saved, bundle)
                st.session_state['calculation_step'] = 0
                st.session_state.pop('boosting_trace', None)
            else:
                st.session_state['presentation_prediction'] = view.one_hour(hourly, at, saved, bundle, mode)
        except (ValueError, OSError) as error:
            st.error(str(error))
    if mode == 'trace':
        st.info('Bấm nút trên để tính thật cho một giờ. Sau đó Tiếp theo hoặc Phát/Dừng để phát lại dấu vết; '
                'không mô phỏng thời gian chạy và không huấn luyện lại.')
        if 'calculation_trace' in st.session_state:
            calculation_panel(st.session_state['calculation_trace'], bundle, reduced)
        return
    if 'presentation_prediction' not in st.session_state:
        return
    result, parts = st.session_state['presentation_prediction']
    if pd.isna(result['prediction']):
        st.warning(result['status'])
        return
    st.caption(f"{result['date_time']} · {'Live inference thật' if mode == 'live' else 'Test đã lưu'}")
    for col, title, field in zip(st.columns(3), ['Dự đoán', 'Thực tế', 'Sai số tuyệt đối'],
                                 ['prediction', 'actual', 'absolute_error']):
        col.metric(title, f"{result[field]:,.2f} xe/giờ")
    if not reduced:
        plot(visual.prediction_animation(result), 'prediction_animation')
    else:
        st.write('C30 → ensemble → dự đoán → thực tế → sai số tuyệt đối.')
    if not parts.empty:
        st.dataframe(parts, hide_index=True, width='stretch')
        st.caption('Dự đoán từng mô hình thật, clip không âm, nhân trọng số và cộng; tổng đã kiểm khớp pipeline.')
    else:
        st.caption('File test chỉ lưu ensemble, không lưu dự đoán từng model; không tạo số thành phần giả.')
    if bundle is not None:
        st.write('Trọng số đã lưu: ' + ' + '.join(f'{name} {weight:.0%}' for name, weight in bundle['spec']['weights'].items()))


def move_calculation(delta=None):
    st.session_state['calculation_step'] = 0 if delta is None else max(0, min(5, st.session_state.get('calculation_step', 0) + delta))


def calculation_panel(trace, bundle, reduced):
    """Manual controls and browser-only animation replay a previously computed trace."""
    step = st.session_state.setdefault('calculation_step', 0)
    st.subheader(f'Bước {step+1}/6 · {calculation.STEPS[step]}')
    st.caption(f"Dấu vết tính thật tại {trace['at']}. Thao tác phía dưới chỉ phát lại, không gọi lại mô hình.")
    previous, following, reset = st.columns(3)
    previous.button('Quay lại bước tính', key='calc_back', on_click=move_calculation, args=(-1,), disabled=step == 0)
    following.button('Tiếp theo bước tính', key='calc_next', on_click=move_calculation, args=(1,), disabled=step == 5)
    reset.button('Phát lại từ đầu', key='calc_reset', on_click=move_calculation)
    st.progress((step+1)/6)
    if not reduced:
        plot(visual.calculation_animation(trace), 'calculation_animation')
        st.caption('Phát/Dừng trên hình chỉ đổi animation; bảng giải thích bên dưới theo nút Quay lại/Tiếp theo. '
                   'Hai cách điều khiển độc lập, không giả vờ kéo chậm model.')
    if step == 0:
        st.dataframe(trace['input'], hide_index=True, width='stretch')
        st.write('Nhận lịch, weather cùng giờ và traffic quá khứ. Chưa mở actual của giờ t để đối chiếu.')
    elif step == 1:
        st.write('Pipeline chung tạo 12 biến lịch + 4 weather số + 11 cờ weather + 3 history.')
        feature_table(trace['features'])
        st.caption('Lag tra đúng timestamp, mean[t−24h,t) cần ít nhất 18 quan sát. Không lấy target t/tương lai.')
    elif step == 2:
        st.success('Đã kiểm: 1 × 30 biến, đúng thứ tự artifact, float32, không NaN/inf và sau mốc fit.')
        st.dataframe(pd.DataFrame({'Thứ tự': range(1,31), 'Đặc trưng': trace['features'].columns,
                                   'Kiểu': trace['features'].dtypes.astype(str).to_numpy()}), hide_index=True)
        st.caption('Nếu kiểm tra không đạt, hệ thống dừng trước khi gọi các model; không tự điền history.')
    elif step == 3:
        st.dataframe(trace['parts'][['Mô hình', 'Dự đoán gốc', 'Sau clip ≥ 0', 'Thời gian (ms)']], hide_index=True, width='stretch')
        st.caption('Số liệu của lần predict thật vừa chạy; thời gian phụ thuộc máy và tải hệ thống, không phải benchmark. '
                   'Không cộng/clip từng cây: clip dự đoán của mỗi mô hình trước ensemble.')
    elif step == 4:
        st.dataframe(trace['parts'][['Mô hình', 'Sau clip ≥ 0', 'Trọng số', 'Sau nhân trọng số']], hide_index=True, width='stretch')
        expression = ' + '.join(f"{r['Trọng số']:.2f} × {r['Sau clip ≥ 0']:.6f}" for _, r in trace['parts'].iterrows())
        st.write(expression + f" = {trace['prediction']:.6f} xe/giờ")
        st.caption('Tính bằng số đầy đủ rồi clip tổng ≥ 0; làm tròn chỉ để hiển thị. Đã đối chiếu kết quả test lưu với sai số ≤ 1e−5.')
    else:
        for col, name, key in zip(st.columns(3), ['Dự đoán', 'Thực tế', 'Sai số tuyệt đối'],
                                  ['prediction','actual','absolute_error']):
            col.metric(name, f"{trace[key]:,.2f} xe/giờ")
        st.write(f"|{trace['prediction']:.6f} − {trace['actual']:.6f}| = {trace['absolute_error']:.6f} xe/giờ")
        st.caption('Actual chỉ được tra sau khi các model đã predict. Đây là đối chiếu một mẫu, không đánh giá test độc lập mới.')
    with st.expander('Xem sâu bên trong mô hình'):
        st.write('Đường đi trong một cây · không đại diện dự đoán của cả rừng')
        name = st.selectbox('Rừng cần xem', ['Random Forest', 'ExtraTrees'], key='trace_forest')
        ntrees = len(bundle['models'][name].estimators_)
        index = st.selectbox('Cây trong rừng', list(range(ntrees)), format_func=lambda i:f'Cây {i+1}/{ntrees}', key='trace_tree_'+name)
        path, value = calculation.tree_path(trace['features'], bundle, name, index)
        st.dataframe(path, hide_index=True, width='stretch')
        st.metric('Dự đoán riêng cây này', f'{value:,.2f} xe/giờ')
        st.caption('Mỗi hàng là một nút thật: feature ≤ ngưỡng đi trái, ngược lại đi phải, tới giá trị lá. '
                   'RF/ExtraTrees lấy trung bình nhiều cây; giá trị tại nút giữa đường không phải dự đoán ensemble.')
        st.write('XGBoost · dự đoán cộng dồn qua các vòng đã huấn luyện')
        if st.button('Tính đường dự đoán qua các vòng boosting', key='trace_boosting'):
            with st.spinner('Đang đọc các prefix của mô hình XGBoost đã lưu…'):
                st.session_state['boosting_trace'] = calculation.boosting_curve(trace['features'], bundle)
        if 'boosting_trace' in st.session_state:
            curve = st.session_state['boosting_trace']
            figure = visual.go.Figure(visual.go.Scatter(x=curve['Vòng đã dùng'], y=curve['Dự đoán XGBoost'], mode='lines'))
            figure.update_layout(xaxis_title='Số vòng boosting đã dùng', yaxis_title='Dự đoán riêng XGBoost · xe/giờ', height=300)
            plot(figure, 'boosting_trace_chart')
            st.dataframe(curve, hide_index=True, width='stretch')
            st.caption('Mỗi điểm dùng iteration_range=(0,k), đã gồm base/intercept và learning rate trong mô hình. '
                       'Không cộng các điểm này với nhau, không nhân learning rate lần nữa. Điểm cuối khớp XGBoost đầy đủ; '
                       'đây là replay inference, không phải lịch sử huấn luyện hoặc đường loss.')


def select_error(at):
    st.session_state['error_at'] = at


@st.fragment
def evaluation_panel(saved, hourly, bundle, token):
    st.subheader('Sai số trên test UCI đã lưu')
    if saved is None:
        st.warning('Chưa có kết quả test hợp lệ để phân tích.')
        return
    minimum, maximum = saved.date_time.min().date(), saved.date_time.max().date()
    left, right = st.columns(2)
    with left:
        first = st.date_input('Từ ngày', value=minimum, min_value=minimum, max_value=maximum, key='error_begin')
    with right:
        last = st.date_input('Đến ngày', value=min(maximum, minimum+pd.Timedelta(days=6)),
                             min_value=minimum, max_value=maximum, key='error_end')
    if first > last:
        st.error('Ngày kết thúc phải sau hoặc bằng ngày bắt đầu.')
        return
    subset = saved.loc[saved.date_time.between(pd.Timestamp(first), pd.Timestamp(last)+pd.Timedelta(hours=23))]
    scope = view.metrics(subset)
    metric_strip(scope)
    st.caption(f"{first} → {last}: chấm {scope['n']}/{scope['n_total']} dòng đã lưu; loại {scope['n_excluded']}. "
               'Đây là metric trong khoảng đang chọn, không gộp validation.')
    valid = subset.loc[subset.prediction.notna() & subset.actual.notna()].copy()
    if valid.empty:
        st.info('Khoảng này chưa có dự đoán đủ điều kiện.')
        return
    valid['absolute_error'] = (valid.prediction-valid.actual).abs()
    if st.session_state.get('error_scope') != (str(first), str(last)):
        for key in ['error_at', 'largest_at']:
            st.session_state.pop(key, None)
        st.session_state['error_scope'] = (str(first), str(last))
    at = st.selectbox('Giờ cần khoanh trên cả hai biểu đồ', valid.date_time.tolist(),
                      index=None if 'error_at' in st.session_state else 0, key='error_at', format_func=str)
    plot(visual.linked_errors(subset, at), 'linked_errors')
    st.caption('Hai viền đỏ cùng một timestamp. Chọn giờ ở trên để xem đồng bộ; kéo/zoom hình để khảo sát. '
               'Giờ không có dữ liệu giữ khoảng trống, không nối đường qua giờ thiếu.')
    st.subheader('Sai số theo nhóm thời gian')
    dimension = st.selectbox('Nhóm để phân tích', ['Giờ', 'Loại ngày', 'Cao điểm'], key='slice_dimension')
    groups = view.error_slices(subset)
    groups = groups.loc[groups['Chiều phân tích'].eq(dimension)]
    st.dataframe(groups, hide_index=True, width='stretch')
    fig = visual.go.Figure(visual.go.Bar(x=groups['Nhóm'], y=groups.MAE, customdata=groups['n'],
        marker_color=visual.BLUE, hovertemplate='%{x}<br>MAE %{y:.2f}<br>n=%{customdata}<extra></extra>'))
    fig.update_layout(height=230, yaxis_title='MAE · xe/giờ', margin=dict(t=5, b=30))
    plot(fig, 'error_slices')
    st.caption('Cao điểm: 06–08 và 15–17, thứ Hai–thứ Sáu, đúng C30. Nhóm n nhỏ/mức lưu lượng khác có thể làm MAE khác; '
               'đây là quan sát, chưa chứng minh weather hoặc ngày lễ gây sai số.')
    largest = valid.nlargest(10, 'absolute_error')
    st.subheader('Những giờ sai số lớn trong khoảng đang chọn')
    st.dataframe(largest[['date_time', 'actual', 'prediction', 'absolute_error']], hide_index=True, width='stretch')
    detail_at = st.selectbox('Xem đầu vào giờ sai số lớn', largest.date_time.tolist(), key='largest_at', format_func=str)
    st.button('Khoanh giờ sai số lớn trên biểu đồ', key='inspect_largest', on_click=select_error, args=(detail_at,))
    with st.expander('C30 của mẫu sai số lớn đang chọn'):
        if bundle is None or hourly is None:
            st.info('Cần artifact và bảng hourly hợp lệ để dựng vector.')
        else:
            try:
                feature_table(features(token, detail_at, hourly, bundle))
            except ValueError as error:
                st.warning(str(error))
    st.download_button('Tải kết quả đã lưu trong khoảng', subset.to_csv(index=False).encode('utf-8'), 'test_scope.csv', 'text/csv')
    with st.expander('Residual và sai số theo ngày'):
        charts.error_charts(subset, 'test UCI · khoảng đang chọn')


@st.fragment
def external_panel(bundle):
    st.subheader('Giới hạn và nghiên cứu mở rộng')
    st.write('Một trạm, dữ liệu thiếu giờ, weather cùng giờ giả định sẵn có. Validation đã được dùng chọn phương án; '
             'điểm test không chứng minh khả năng tổng quát sang nguồn mới hoặc dự báo live nhiều bước.')
    for message in demo.BLOCKERS.values():
        st.warning(message)
    if st.button('Kiểm tra và mở MnDOT + OpenWeather', key='open_external'):
        st.session_state['external_open'] = True
    if st.session_state.get('external_open'):
        try:
            paths = [demo.TRAFFIC, demo.WEATHER, ow.RAW, ow.SUMMARY, ow.AUDIT, demo.MANIFEST,
                     demo.MNDOT/'prepared/atr301_westbound_2018_hourly.csv']
            token = demo.file_token(paths)
            if st.session_state.get('external_token') != token:
                st.session_state.pop('external_comparison', None)
                st.session_state.pop('external_weather_comparison', None)
                st.session_state['external_token'] = token
            context, traffic, weather, end = external_sources(token)
            policy = st.selectbox('Giả định thời gian để kiểm tra ghép', ow.POLICIES, key='external_policy')
            joined = preview(token, policy, context, weather, end)
            new = joined.loc[joined.date_time.gt(end)]
            matched = int(new[ow.VALUES].notna().all(axis=1).sum())
            history = demo.add_history_features(joined).loc[lambda x: x.date_time.gt(end)]
            plot(visual.pipeline(['Nguồn', 'Chuẩn giờ', 'Ghép', 'Kiểm tra', 'Inference'],
                [f'{len(traffic)} / {len(weather)}', policy.split(' · ')[0], f'{matched}/{len(new)} giờ',
                 f'{int(new.is_holiday.isna().sum())} thiếu lễ', 'Chưa đủ điều kiện'], active=2), 'external_pipeline')
            expected = len(pd.date_range(new.date_time.min(), new.date_time.max(), freq='h'))
            counts = pd.DataFrame([
                ['Traffic sau UCI', len(new), expected-len(new), 'Giờ traffic vắng giữ vắng'],
                ['Weather UTC', len(weather), 0, 'Trang nguồn và cờ zero có provenance'],
                ['Chuẩn giờ traffic', int(new.date_time_utc.notna().sum()), int(new.date_time_utc.isna().sum()),
                 'Giữ timestamp gốc, không tự chọn offset DST'],
                ['Ghép theo giả định', matched, len(new)-matched, 'Chicago giữ thiếu giờ DST mơ hồ'],
                ['History traffic', int(history[demo.HISTORY_FEATURES].notna().all(axis=1).sum()),
                 int(history[demo.HISTORY_FEATURES].isna().any(axis=1).sum()), 'Không điền lag/traffic'],
                ['Ngày lễ', int(new.is_holiday.notna().sum()), int(new.is_holiday.isna().sum()), 'Không tự đặt ngày thường']],
                columns=['Bước', 'Có dữ liệu', 'Thiếu/không ghép', 'Giải thích'])
            st.dataframe(counts, hide_index=True, width='stretch')
            st.metric('Weather ghép được theo giả định', f'{matched/len(new):.2%}')
            st.caption('Các nhóm thiếu có thể chồng lấn. Tỷ lệ ghép không phải tỷ lệ đủ điều kiện inference.')
            with st.expander('Xem dữ liệu sau ghép và metadata nguồn'):
                st.dataframe(new, width='stretch')
                st.json(demo.json_file(ow.SUMMARY))
                st.json(demo.json_file(demo.MANIFEST))
            st.button('Dự đoán MnDOT · chưa đủ điều kiện', disabled=True, key='external_predict')
            if st.button('Đối chiếu traffic UCI–MnDOT', key='compare_sources'):
                st.session_state['external_comparison'] = demo.source_comparison()
            if 'external_comparison' in st.session_state:
                charts.source_charts(st.session_state['external_comparison'])
            if st.button('Đối chiếu weather OpenWeather–UCI', key='compare_weather'):
                st.session_state['external_weather_comparison'] = (policy, ow.compare(demo.read_hourly(demo.UCI), weather, policy))
            if st.session_state.get('external_weather_comparison', (None,))[0] == policy:
                charts.weather_charts(st.session_state['external_weather_comparison'][1])
        except (OSError, ValueError, KeyError) as error:
            st.error(f'Không mở được nguồn ngoài: {error}. Luồng UCI vẫn hoạt động.')
    with st.expander('Nâng cao · kiểm tra phần mềm bằng dữ liệu tổng hợp'):
        st.caption('Fixture nhân tạo, không dùng để kết luận chất lượng mô hình.')
        if st.button('Thử một giờ tổng hợp đủ history', key='fixture_predict', disabled=bundle is None):
            result, parts = demo.components(demo.synthetic_hourly(), pd.Timestamp('2019-01-08'), bundle, compatible=True)
            st.dataframe(result, hide_index=True)
            st.dataframe(parts, hide_index=True)
    for name in ['demo_sources.md', 'demo_data_contract.md', 'weather_integration.md']:
        with st.expander(name):
            st.markdown((demo.ROOT/'docs'/name).read_text(encoding='utf-8'))


def main():
    st.set_page_config(page_title='Metro C30 · từ dữ liệu đến dự đoán', page_icon=':material/route:', layout='wide')
    st.html('<style>[data-testid="stMainBlockContainer"]{max-width:1380px;padding-top:2rem}</style>')
    st.title('Metro C30 / từ dữ liệu đến dự đoán')
    st.caption('I-94 hướng Tây · ATR 301 · đánh giá tuần tự theo giờ trên UCI')
    paths = [demo.UCI_RAW, demo.UCI, demo.ARTIFACT, demo.FINAL/'selected_model.json', demo.FINAL/'final_fit_plan.json',
             demo.FINAL/'test_evaluation.json', demo.FINAL/'test_metrics.csv', demo.FINAL/'test_predictions.csv']
    token = demo.file_token(paths)
    raw = hourly = saved = report = measured = bundle = None
    failures = {}
    try:
        raw, hourly = uci(token)
    except (OSError, ValueError) as error:
        failures['UCI'] = str(error)
    try:
        saved, report, measured = results(token)
    except (OSError, ValueError, KeyError) as error:
        failures['Kết quả test'] = str(error)
    try:
        bundle = model(token)
    except Exception as error:
        failures['Live inference'] = str(error)
    with st.sidebar:
        st.header('Trình diễn trên UCI')
        st.selectbox('Nguồn chính', ['UCI gốc · toàn bộ dữ liệu'], key='source')
        st.caption('MnDOT + OpenWeather ở tab 6. Mặc định đọc dự đoán test đã lưu.')
        reduced = st.checkbox('Giảm chuyển động · thao tác thủ công', key='reduced_motion')
        browse_all = st.checkbox('Nâng cao · chọn cả giờ ngoài test', key='browse_all')
        candidates = (saved.loc[saved.prediction.notna() & saved.actual.notna(), 'date_time'].tolist()
                      if saved is not None and not browse_all else hourly.date_time.tolist() if hourly is not None else [])
        if candidates:
            if st.session_state.get('at') not in candidates:
                st.session_state.pop('at', None)
            at = pd.Timestamp(st.selectbox('Giờ đang trình diễn', candidates,
                index=None if 'at' in st.session_state else 0, format_func=str, key='at'))
            st.caption('Giờ này dùng chung ở tab 3/4. Tab 5 có khoảng chọn riêng để khảo sát sai số.')
        else:
            at = None
            st.warning('Chưa có giờ dữ liệu hợp lệ để chọn.')
        if failures:
            with st.expander('Thành phần chưa khả dụng', expanded=True):
                for name, error in failures.items():
                    st.warning(f'{name}: {error}')
    tabs = st.tabs(['1 · Tổng quan', '2 · Dữ liệu & tiền xử lý', '3 · Lịch sử & C30',
                    '4 · Kết quả dự đoán', '5 · Sai số', '6 · Giới hạn & mở rộng'])
    with tabs[0]:
        st.header('Dự đoán số xe đi qua trạm trong một giờ')
        st.write('UCI Metro Interstate Traffic Volume ghi lưu lượng tại một trạm trên I-94. C30 dùng lịch, '
                 'weather và traffic đã quan sát trong quá khứ để dự đoán traffic_volume, đơn vị xe/giờ.')
        st.markdown('[Nguồn UCI và DOI](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) · '
                    'John Hogue, 2019 · CC BY 4.0')
        if measured is not None:
            st.subheader('Kết quả test đã kiểm chứng')
            metric_strip(measured)
            st.caption(f"{report['metrics']['model']} · chấm {measured['n']}/{measured['n_total']} giờ, loại {measured['n_excluded']}. "
                       f"{report['metrics']['start']} → {report['metrics']['end']}.")
            st.caption('Nguồn: final_C30/test_predictions.csv, test_metrics.csv và test_evaluation.json; '
                       'đã đối chiếu hash và tính lại metric từ file lưu. R² không phải tỷ lệ dự đoán đúng.')
        if bundle is not None:
            st.write('Ensemble: ' + ' + '.join(f'{name} {weight:.0%}' for name, weight in bundle['spec']['weights'].items()))
            st.caption(f"Refit {bundle['n_fit']:,} giờ train + validation đủ history, đến {bundle['train_end']}.")
        if hourly is not None:
            st.dataframe(splits(token, hourly), hide_index=True, width='stretch')
        plot(visual.pipeline(['UCI gốc', 'Làm sạch', 'C30', 'Dự đoán', 'Sai số', 'Giới hạn']), 'overview_pipeline')
        st.info('Kịch bản: từng giờ sử dụng traffic quá khứ đã quan sát và giả định weather cùng giờ sẵn có. '
                'Chưa phải dự báo vận hành nhiều bước với weather biết trước.')
        with st.expander('Bằng chứng phiên bản và trạng thái thành phần'):
            st.write({'raw': str(demo.UCI_RAW), 'hourly': str(demo.UCI), 'artifact': str(demo.ARTIFACT),
                      'artifact_sha256': dict(token).get(str(demo.ARTIFACT)), 'lỗi_thành_phần': failures})
    with tabs[1]:
        walkthrough(raw, hourly, token, at, reduced)
    with tabs[2]:
        if at is not None:
            history_panel(hourly, at, bundle, token)
        else:
            st.info('Cần dữ liệu hợp lệ để xem đầu vào theo giờ.')
    with tabs[3]:
        if at is not None:
            prediction_panel(hourly, saved, bundle, at, token, reduced)
        else:
            st.info('Chưa có giờ test hoặc kết quả lưu để trình diễn.')
    with tabs[4]:
        evaluation_panel(saved, hourly, bundle, token)
    with tabs[5]:
        external_panel(bundle)
