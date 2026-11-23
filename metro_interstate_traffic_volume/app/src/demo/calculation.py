"""True single-hour inference traces; never fit or modify the frozen pipeline."""
from time import perf_counter
import numpy as np
import pandas as pd
from . import presentation as view

STEPS = ['Nhận đầu vào', 'Tạo C30', 'Kiểm tra đầu vào',
         'Chạy từng mô hình', 'Tính ensemble', 'Đối chiếu thực tế']


def run(hourly, at, saved, bundle):
    """Compute first, then return a trace suitable for honest step-by-step replay.

    Actual is looked up only after inference. Per-model timings cover predict()
    plus clipping for one call; they are observations, not benchmark results.
    """
    if bundle is None:
        raise ValueError('Cần artifact hợp lệ để tính và giải thích.')
    at = pd.Timestamp(at)
    matrix = view.inspected_features(hourly, at, bundle)
    values = np.ascontiguousarray(matrix, dtype='float32')
    if values.shape != (1, 30) or not np.isfinite(values).all():
        raise ValueError('Chưa đủ 30 đầu vào hữu hạn; dừng trước khi gọi mô hình.')
    rows = []
    for name, estimator in bundle['models'].items():
        started = perf_counter()
        raw = estimator.predict(values)
        clipped = np.clip(raw, 0, None).astype('float64')[0]
        elapsed = (perf_counter() - started) * 1000
        weight = bundle['spec']['weights'][name]
        rows.append({'Mô hình': name, 'Dự đoán gốc': float(raw[0]),
                     'Sau clip ≥ 0': float(clipped), 'Trọng số': weight,
                     'Sau nhân trọng số': float(clipped * weight), 'Thời gian (ms)': elapsed})
    parts = pd.DataFrame(rows)
    predicted = float(np.clip(np.sum(parts['Sau nhân trọng số'].to_numpy()), 0, None))
    # The actual at t is not inspected until the model calls have completed.
    selected = saved.loc[saved.date_time.eq(at)]
    if len(selected) != 1 or not np.isfinite(selected.prediction.iloc[0]):
        raise ValueError('Cần giờ test có kết quả lưu để đối chiếu trace.')
    reference = selected.iloc[0]
    if not np.isclose(predicted, reference.prediction, rtol=0, atol=1e-5):
        raise ValueError('Trace không khớp ensemble đã lưu; không trình bày như kết quả hợp lệ.')
    return {'at': at, 'features': matrix, 'parts': parts, 'prediction': predicted,
            'actual': float(reference.actual), 'absolute_error': abs(predicted-reference.actual),
            'input': hourly.loc[hourly.date_time.eq(at), ['date_time', 'temp', 'rain_1h', 'snow_1h',
                                                        'clouds_all', 'weather_main', 'is_holiday']].copy()}


def tree_path(features, bundle, name, tree_index):
    """Trace root-to-leaf using the estimator's actual decision_path and apply."""
    if name not in ('Random Forest', 'ExtraTrees'):
        raise ValueError('Chỉ xem cây của Random Forest hoặc ExtraTrees.')
    forest = bundle['models'][name]
    if not 0 <= tree_index < len(forest.estimators_):
        raise ValueError('Chỉ số cây ngoài phạm vi.')
    tree = forest.estimators_[tree_index]
    array = np.ascontiguousarray(features, dtype='float32')
    nodes = tree.decision_path(array).indices
    leaf = int(tree.apply(array)[0])
    rows = []
    for depth, node in enumerate(nodes):
        is_leaf = node == leaf
        feature_index = tree.tree_.feature[node]
        threshold = tree.tree_.threshold[node]
        value = None if is_leaf else float(array[0, feature_index])
        left = not is_leaf and value <= threshold
        next_node = None if is_leaf else int(tree.tree_.children_left[node] if left else tree.tree_.children_right[node])
        rows.append({'Bước': depth + 1, 'Nút': int(node),
                     'Đặc trưng': 'Lá kết thúc' if is_leaf else bundle['features'][feature_index],
                     'Giá trị mẫu': value, 'Ngưỡng ≤': None if is_leaf else float(threshold),
                     'Hướng đi': 'Kết thúc' if is_leaf else 'Trái (≤)' if left else 'Phải (>)',
                     'Nút kế tiếp': next_node,
                     'Giá trị tại nút/lá': float(tree.tree_.value[node].ravel()[0])})
    value = float(tree.predict(array)[0])
    if not np.isclose(value, rows[-1]['Giá trị tại nút/lá']):
        raise ValueError('Đường đi không khớp giá trị lá.')
    return pd.DataFrame(rows), value


def boosting_curve(features, bundle):
    """Replay prediction with prefixes of already-trained rounds, not training.

    iteration_range=(0,k) includes the base/intercept and first k rounds. Never
    sum these prefix predictions or multiply learning_rate a second time.
    """
    estimator = bundle['models']['XGBoost']
    rounds = estimator.get_booster().num_boosted_rounds()
    array = np.ascontiguousarray(features, dtype='float32')
    rows = [{'Vòng đã dùng': k, 'Dự đoán XGBoost': float(estimator.predict(array, iteration_range=(0, k))[0])}
            for k in range(1, rounds + 1)]
    frame = pd.DataFrame(rows)
    full = float(estimator.predict(array)[0])
    if not np.isclose(frame['Dự đoán XGBoost'].iloc[-1], full, rtol=0, atol=1e-5):
        raise ValueError('Prefix cuối không khớp XGBoost đầy đủ.')
    frame['Thay đổi so vòng trước'] = frame['Dự đoán XGBoost'].diff()
    return frame
