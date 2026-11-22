"""Write the current data/artifact audit without training or scoring UCI."""

from . import service as demo


def main():
    bundle, error = None, None
    try:
        bundle = demo.audited_bundle()
    except Exception as exc:
        error = str(exc)
    table = demo.audit(bundle, error)
    context, traffic, weather, uci_end = demo.load_sources()
    _, counts = demo.quality_grid(context, traffic.date_time.min(), traffic.date_time.max())
    output = demo.ROOT / 'docs/demo_audit.md'
    columns = table.columns.tolist()
    lines = ['# Bảng kiểm tra demo', '', 'Tạo từ file thật; không huấn luyện, dự đoán hoặc chấm lại UCI.', '',
             '| ' + ' | '.join(columns) + ' |', '| ' + ' | '.join(['---'] * len(columns)) + ' |']
    for values in table.itertuples(index=False, name=None):
        lines.append('| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', ' ') for v in values) + ' |')
    lines += ['', '## MnDOT sau UCI', '', f'Mốc cuối UCI: {uci_end}. Weather UTC chưa ghép: {len(weather)} giờ.', '',
              '| Chỉ tiêu | Số giờ |', '| --- | ---: |']
    lines += [f'| {key} | {value} |' for key, value in counts.items()]
    lines += ['', 'Nhóm thiếu có thể chồng lấn. Đủ history chưa đồng nghĩa đủ đầu vào C30.', '',
              'Xem [hợp đồng và phương án cần quyết định](demo_data_contract.md).']
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
