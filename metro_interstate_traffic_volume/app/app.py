"""Run from the repository root: python -m streamlit run app/app.py."""

from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import pandas as pd
import streamlit as st

from app.src.demo import service as demo
from app.src.demo import charts

st.set_page_config(page_title='Metro · C30', page_icon=':material/route:', layout='wide')


@st.cache_resource(show_spinner='Đang xác minh artifact cuối…')
def cached_model(token):
    return demo.audited_bundle()


@st.cache_data(show_spinner='Đang đọc dữ liệu nguồn…')
def cached_sources(token):
    return demo.load_sources()


@st.cache_data(show_spinner=False)
def cached_audit(token, _bundle, error):
    return demo.audit(_bundle, error)


@st.cache_data(show_spinner=False)
def cached_quality(token, source, start, end, _hourly, _bundle, compatible):
    return demo.quality_grid(_hourly, start, end, _bundle, compatible)


@st.cache_data(show_spinner='Đang đối chiếu nguồn traffic…')
def cached_comparison(token):
    # v2: separate timestamp coverage from value agreement on the intersection.
    return demo.source_comparison()


@st.cache_data(show_spinner='Đang đọc dự đoán test đã lưu…')
def cached_test_predictions(token):
    return demo.saved_test_predictions()


def invalidate(key, signature):
    """Remove outputs immediately when source/time/file identities change."""
    if st.session_state.get(key + '_signature') != signature:
        st.session_state.pop(key, None)
        st.session_state[key + '_signature'] = signature


def show_counts(counts):
    st.dataframe(pd.DataFrame({'Chỉ tiêu': counts.keys(), 'Số giờ': counts.values()}),
                 hide_index=True, width='stretch')


def plot_gaps(frame):
    """Explicit segments prevent interpolation across missing hourly values."""
    charts.lines_with_gaps(frame[['traffic_volume', 'prediction']])


def main():
    st.title('Metro / C30')
    st.caption('I-94 · ATR 301 · hướng Tây · xe/giờ')
    st.info('Mô phỏng dự đoán theo giờ trên dữ liệu lịch sử, sử dụng thời tiết tái phân tích cùng giờ.')
    st.caption('ERA5 chỉ có ở nguồn ngoài đang kiểm tra. Đây chưa phải dự báo vận hành với weather biết trước.')

    paths = [demo.ARTIFACT, demo.FINAL / 'selected_model.json', demo.FINAL / 'final_fit_plan.json',
             demo.FINAL / 'test_evaluation.json', demo.FINAL / 'test_metrics.csv',
             demo.FINAL / 'test_predictions.csv', demo.UCI,
             demo.TRAFFIC, demo.WEATHER, demo.MANIFEST,
             demo.MNDOT / 'raw/atr_2018.csv',
             demo.MNDOT / 'prepared/atr301_westbound_2018_hourly.csv',
             demo.MNDOT / 'weather/request_metadata.json',
             *[PROJECT / p for p in ['predict.py', 'src/features.py', 'src/preprocessing.py', 'src/feature_experiments.py']]]
    token = demo.file_token(paths)
    bundle, model_error = None, None
    try:
        bundle = cached_model(token)
    except Exception as error:
        model_error = str(error)
        st.error(f'Không dùng được artifact: {error}. Dữ liệu vẫn có thể xem trước.')
    try:
        context, traffic, weather, uci_end = cached_sources(token)
    except (OSError, ValueError) as error:
        st.error(f'Không đọc được nguồn dữ liệu: {error}')
        st.stop()

    with st.sidebar:
        st.header('Nguồn dữ liệu')
        source = st.selectbox('Chọn nguồn', ['MnDOT 2018 · đang kiểm tra', 'Tổng hợp · kiểm tra kỹ thuật'], key='source')
        artificial = source.startswith('Tổng hợp')
        st.warning('Dữ liệu tổng hợp chỉ kiểm tra ứng dụng; không dùng để báo cáo chất lượng mô hình.'
                   if artificial else 'Dự đoán MnDOT đang khóa: weather, thời gian và ngày lễ chưa đạt hợp đồng.')
        st.caption('Không huấn luyện lại. Test UCI chỉ đọc kết quả đã lưu.')
    hourly = demo.synthetic_hourly() if artificial else context
    candidates = hourly.date_time if artificial else traffic.date_time
    start, end = candidates.min(), candidates.max()
    compatible = artificial  # No UI toggle can certify MnDOT compatibility.
    ready = compatible and bundle is not None

    tabs = st.tabs(['1 · Tổng quan', '2 · Dữ liệu', '3 · Giờ & history',
                    '4 · Mô hình & dự đoán', '5 · Đánh giá', '6 · Hướng dẫn'])
    with tabs[0]:
        st.subheader('Bảng kiểm tra trước triển khai')
        st.dataframe(cached_audit(token, bundle, model_error), hide_index=True, width='stretch')
        st.caption('Ba trạng thái phân biệt: đã xác minh / có nhưng chưa tương thích / chưa có dữ liệu.')
        st.markdown('**Luồng:** nguồn → hợp đồng dữ liệu → bảng giờ + context → `prepare_features` → `predict_hours`.')

    with tabs[1]:
        st.subheader('Độ phủ dữ liệu theo giờ')
        st.caption(f'Phạm vi: {start} → {end}. Nguồn hiện chọn: {source}. Context được giữ trước khi lọc.')
        grid, counts = cached_quality(token, source, start, end, hourly, bundle, compatible)
        show_counts(counts)
        st.caption('Các nhóm thiếu có thể chồng lấn. Không cộng chúng thành tổng giờ bị loại.')
        cols = ['traffic_volume', 'has_record', 'has_target', 'has_history', 'missing_weather_raw',
                'compatible_weather', 'input_ready', 'score_ready']
        st.dataframe(grid[cols], width='stretch')
        st.caption('Giờ vắng được thêm vào lưới để kiểm tra; không thêm vào dữ liệu inference và không điền traffic/history.')
        with st.expander('Traffic gốc và provenance'):
            st.dataframe(hourly.loc[hourly.date_time.between(start, end)], width='stretch')
            if not artificial:
                st.json(demo.json_file(demo.MANIFEST))
        if not artificial:
            with st.expander('Weather ERA5 nguyên trạng · UTC · chưa ghép'):
                st.dataframe(weather, width='stretch')
                st.json(demo.json_file(demo.MNDOT / 'weather/request_metadata.json'))
            st.divider()
            invalidate('comparison_result', (token, 'coverage-v2'))
            if st.button('Lập biểu đồ đối chiếu nguồn', key='compare_sources'):
                st.session_state['comparison_result'] = cached_comparison(token)
            if 'comparison_result' in st.session_state:
                charts.source_charts(st.session_state['comparison_result'])

    with tabs[2]:
        st.subheader('Quan sát một giờ')
        # Reset the widget if its source changes; values are timestamps, not row positions.
        if st.session_state.get('hour_source') != source:
            st.session_state.pop('at', None)
            st.session_state['hour_source'] = source
        default = min(168, len(candidates) - 1) if artificial else 0
        at = st.selectbox('Giờ cần xem', candidates.tolist(), index=default, key='at', format_func=str)
        at = pd.Timestamp(at)
        window = demo.history_window(hourly, at)
        st.caption(f'mean_24h: [{at - pd.Timedelta(hours=24)}, {at}) · '
                   f'{window.traffic_volume.notna().sum()}/24 quan sát · cần ít nhất 18.')
        st.dataframe(grid.loc[[at], ['lag_24h', 'lag_168h', 'mean_24h', 'has_history']], width='stretch')
        with st.expander('Các quan sát tham gia cửa sổ mean_24h'):
            st.dataframe(window, hide_index=True, width='stretch')
        if bundle is not None:
            values = demo.weather_values(hourly, at, bundle, compatible)
            if artificial:
                values['Trạng thái'] = values['Trạng thái'].replace({'Quan sát trực tiếp': 'Giá trị tổng hợp (fixture)'})
            st.dataframe(values, hide_index=True, width='stretch')
        st.caption('Giá trị tại t và tương lai không dùng để tạo history tại t. Weather tổng hợp là fixture, không phải đo trực tiếp.')
        if st.button('Xem C30 dẫn xuất', disabled=not ready, key='features'):
            features = demo.prepare_features(hourly, [at], bundle)
            st.dataframe(features.T.rename(columns={at: 'Giá trị'}), width='stretch')
            st.caption('Đúng thứ tự artifact; đây là dữ liệu dẫn xuất, không thay thế context.')

    signature = (token, source, str(at))
    invalidate('prediction_result', signature)
    with tabs[3]:
        st.subheader('Artifact cuối và ensemble')
        st.code(str(demo.ARTIFACT.relative_to(PROJECT)))
        if bundle is not None:
            st.caption(f"Kết thúc fit: {bundle['train_end']} · {bundle['n_fit']:,} giờ đủ history · train + validation")
            st.caption('Không có metadata đáng tin cậy về thời điểm tạo artifact; không dùng thời gian sửa file.')
            st.code(dict(token)[str(demo.ARTIFACT)], language=None)
            st.dataframe(pd.DataFrame([{'Mô hình': n, 'Trọng số': w} for n, w in bundle['spec']['weights'].items()]),
                         hide_index=True, width='stretch')
            with st.expander('C30 và thống kê điền thiếu đã khóa'):
                st.dataframe(pd.DataFrame({'Thứ tự': range(1, 31), 'Đặc trưng': bundle['features']}), hide_index=True)
                stats = bundle['fill_statistics']
                st.write({'temp_fallback_K': stats['temp_fallback'], 'rain_median_mm': stats['rain_median']})
                st.dataframe(stats['temp_by_month_hour'].rename('temp_K').reset_index())
        st.caption(f'Giờ đang chọn: {at} · {source}')
        if not compatible:
            st.warning('Khóa dự đoán ngoài. Xem các vấn đề cần quyết định ở tab Hướng dẫn.')
        if st.button('Dự đoán giờ đã chọn', key='predict', disabled=not ready):
            with st.spinner('Đang dự đoán một giờ…'):
                st.session_state['prediction_result'] = demo.components(hourly, at, bundle, compatible)
        if 'prediction_result' in st.session_state:
            result, parts = st.session_state['prediction_result']
            if parts.empty:
                st.warning(str(result.status.iloc[0]))
            else:
                st.metric('Dự đoán · xe/giờ', f'{result.prediction.iloc[0]:,.1f}')
                st.dataframe(parts, hide_index=True, width='stretch')
                st.caption('Phép tính ensemble, không phải đóng góp đặc trưng. Clip từng mô hình rồi cộng trọng số như predict.py.')
                st.caption('Tổng thành phần đã được kiểm tra khớp dự đoán gốc; làm tròn chỉ để hiển thị.')

    with tabs[4]:
        st.subheader('Test UCI · chỉ đọc kết quả đã lưu')
        metrics_path = demo.FINAL / 'test_metrics.csv'
        report = demo.json_file(demo.FINAL / 'test_evaluation.json')
        if demo.sha256(metrics_path) == report['output_sha256']['test_metrics.csv']:
            st.dataframe(pd.read_csv(metrics_path), hide_index=True, width='stretch')
        else:
            st.error('Hash bảng test đã thay đổi; không hiển thị như kết quả đã xác minh.')
        invalidate('saved_error_view', token)
        if st.button('Xem biểu đồ sai số UCI đã lưu', key='saved_errors'):
            st.session_state['saved_error_view'] = True
        if st.session_state.get('saved_error_view'):
            try:
                charts.error_charts(cached_test_predictions(token), 'test UCI đã lưu · không dự đoán/chấm lại')
            except ValueError as error:
                st.error(str(error))
        st.divider()
        st.subheader('Kiểm tra cơ chế chấm · dữ liệu tổng hợp' if artificial else 'MnDOT · đánh giá ngoài')
        st.caption('Hai nguồn khác giai đoạn, weather và số mẫu. Không suy ra phần trăm cải thiện giữa chúng.')
        default_begin = start + pd.Timedelta(hours=168) if artificial else start
        range_start = st.date_input('Từ ngày', value=default_begin.date(), min_value=start.date(), max_value=end.date(), key=f'begin_{artificial}')
        range_end = st.date_input('Đến ngày', value=min(end, default_begin + pd.Timedelta(days=2)).date(),
                                  min_value=start.date(), max_value=end.date(), key=f'end_{artificial}')
        begin = max(start, pd.Timestamp(range_start))
        finish = min(end, pd.Timestamp(range_end) + pd.Timedelta(hours=23))
        range_signature = (token, source, str(begin), str(finish))
        invalidate('evaluation_result', range_signature)
        valid_range = begin <= finish
        if not valid_range:
            st.error('Ngày kết thúc phải sau hoặc bằng ngày bắt đầu.')
        if not compatible:
            st.warning('Chưa thể đánh giá MnDOT: không dùng imputer để che khác biệt nguồn weather.')
        if st.button('Đánh giá khoảng đã chọn', key='evaluate', disabled=not ready or not valid_range):
            with st.spinner('Đang đánh giá khoảng đã chọn…'):
                st.session_state['evaluation_result'] = demo.evaluate_range(hourly, begin, finish, bundle, uci_end, compatible)
        if 'evaluation_result' in st.session_state:
            scored_grid, scoped_counts, values = st.session_state['evaluation_result']
            st.caption(f'Kết quả thuộc khoảng {begin} → {finish} · {source}')
            st.write(values)
            show_counts(scoped_counts)
            plot_gaps(scored_grid)
            charts.error_charts(scored_grid.reset_index().rename(columns={'traffic_volume': 'actual'}),
                                'fixture tổng hợp · không phải MnDOT' if artificial else 'MnDOT · khoảng đang chọn')
            st.caption('Các lý do loại có thể chồng lấn; tổng loại dùng hợp duy nhất. Khoảng thiếu được giữ trên biểu đồ.')
            st.dataframe(scored_grid.nlargest(10, 'absolute_error').dropna(subset=['absolute_error']), width='stretch')
            st.caption('Sai số lớn chỉ gợi ý khảo sát; chưa đủ để kết luận nguyên nhân. Dữ liệu tổng hợp không đo chất lượng ngoài.')
            st.download_button('Tải kết quả khoảng đang chọn', scored_grid.to_csv().encode('utf-8'), 'range_preview.csv', 'text/csv')

    with tabs[5]:
        st.markdown((Path(__file__).parent / 'docs/demo_sources.md').read_text(encoding='utf-8'))
        st.divider()
        st.subheader('Điều kiện mở dự đoán MnDOT')
        for message in demo.BLOCKERS.values():
            st.warning(message)
        st.markdown('**Phương án:** ưu tiên weather có định nghĩa gần UCI; hoặc thiết kế thử nghiệm chuyển nguồn ERA5 '
                    'với mapping xấp xỉ được công bố. Cả hai cần chốt timezone/DST và lịch sự kiện trước khi ghép.')
        st.caption('Không có nút bỏ qua kiểm tra tương thích. Đổi nguồn/giờ/khoảng tự xóa kết quả cũ.')
        for name in ['demo_data_contract.md', 'demo_examples.md', 'noaa_review.md', 'openweather_review.md']:
            with st.expander(name):
                st.markdown((Path(__file__).parent / 'docs' / name).read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
