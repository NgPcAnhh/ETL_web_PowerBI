import pandas as pd
import os
import re

def process_balancesheet_from_config(config_path):
    # Đọc config
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    config = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip().strip('"\'')
    # Lấy thông tin cần thiết
    output_dir = config.get('output_dir', '')
    IDcp = config.get('ma_cp', '') or config.get('IDcp', '')
    start = config.get('start', '')
    end = config.get('end', '')

    # Đường dẫn file balance sheet
    balance_sheet_path = os.path.join(output_dir, f"{IDcp}_balance_sheet.csv")
    if not os.path.exists(balance_sheet_path):
        print(f"Không tìm thấy file: {balance_sheet_path}")
        return False

    # Đọc dữ liệu, đảm bảo cột Quý là text
    df = pd.read_csv(balance_sheet_path, dtype={'Quý': str})
    df = df.fillna('')

    # Tách cột Quý thành 2 cột: Quý và Năm
    def split_quarter(q):
        m = re.match(r"'?(\d+)/(\d+)", str(q))
        if m:
            return m.group(1), m.group(2)
        return '', ''
    df[['Quý_moi', 'Năm']] = df['Quý'].apply(split_quarter).apply(pd.Series)
    df['Quý'] = df['Quý_moi']
    df.drop(columns=['Quý_moi'], inplace=True)

    # Lọc theo khoảng thời gian
    def quarter_to_tuple(q, y):
        try:
            return (int(y), int(q))
        except:
            return (0, 0)
    start_q, start_y = split_quarter(start)
    end_q, end_y = split_quarter(end)
    start_tuple = quarter_to_tuple(start_q, start_y)
    end_tuple = quarter_to_tuple(end_q, end_y)
    df['__quarter_tuple'] = df.apply(lambda row: quarter_to_tuple(row['Quý'], row['Năm']), axis=1)
    df = df[(df['__quarter_tuple'] >= start_tuple) & (df['__quarter_tuple'] <= end_tuple)].copy()
    df = df.drop(columns='__quarter_tuple')

    # Đổi tên các cột cần lấy cho dễ xử lý
    col_map = {
        'Tiền và các khoản tương đương tiền': 'I. Tiền và các khoản tương đương tiền',
        'Các khoản đầu tư tài chính ngắn hạn': 'II. Các khoản đầu tư tài chính ngắn hạn',
        'Các khoản phải thu ngắn hạn': 'III. Các khoản phải thu ngắn hạn',
        'Hàng tồn kho': 'IV. Hàng tồn kho',
        'Tài sản ngắn hạn khác': 'V.Tài sản ngắn hạn khác',
        'Các khoản phải thu dài hạn': 'I. Các khoản phải thu dài hạn',
        'Tài sản cố định': 'II.Tài sản cố định',
        'Tài sản dở dang dài hạn': 'IV. Tài sản dở dang dài hạn',
        'Bất động sản đầu tư': 'III. Bất động sản đầu tư',
        'Đầu tư tài chính dài hạn': 'V. Đầu tư tài chính dài hạn',
        'Tài sản dài hạn khác': 'VI. Tài sản dài hạn khác',
        'Nợ ngắn hạn': 'I. Nợ ngắn hạn',
        'Nợ dài hạn': 'II. Nợ dài hạn',
        'Vốn chủ sở hữu': 'I. Vốn chủ sở hữu',
        'Nguồn kinh phí và quỹ khác': 'II. Nguồn kinh phí và quỹ khác',
        'Tổng nợ': 'C. NỢ PHẢI TRẢ',
        'Tổng tài sản': 'TỔNG CỘNG TÀI SẢN',
        'Tài sản ngắn hạn': 'A- TÀI SẢN NGẮN HẠN',
    }

    # Đảm bảo các cột cần thiết tồn tại
    for v in col_map.values():
        if v not in df.columns:
            df[v] = ''

    # Chuyển đổi về số
    def to_num(x):
        try:
            return float(str(x).replace(',', '').replace(' ', ''))
        except:
            return 0

    # Tính các chỉ số tài chính
    result = []
    for idx, row in df.iterrows():
        try:
            tong_no = to_num(row[col_map['Tổng nợ']])
            tong_taisan = to_num(row[col_map['Tổng tài sản']])
            von_chu_so_huu = to_num(row[col_map['Vốn chủ sở hữu']])
            no_dai_han = to_num(row[col_map['Nợ dài hạn']])
            no_ngan_han = to_num(row[col_map['Nợ ngắn hạn']])
            taisan_nganhan = to_num(row[col_map['Tài sản ngắn hạn']])
            hang_ton_kho = to_num(row[col_map['Hàng tồn kho']])

            # Chỉ số
            debt_ratio = tong_no / tong_taisan if tong_taisan else ''
            de_ratio = tong_no / von_chu_so_huu if von_chu_so_huu else ''
            asset_leverage = tong_taisan / von_chu_so_huu if von_chu_so_huu else ''
            equity_to_asset = von_chu_so_huu / tong_taisan if tong_taisan else ''
            long_debt_to_equity = no_dai_han / von_chu_so_huu if von_chu_so_huu else ''
            financial_leverage = tong_no / von_chu_so_huu if von_chu_so_huu else ''
            current_ratio = taisan_nganhan / no_ngan_han if no_ngan_han else ''
            quick_ratio = (taisan_nganhan - hang_ton_kho) / no_ngan_han if no_ngan_han else ''

            # Lấy các cột cần giữ lại
            keep_cols = [
                'Quý', 'Năm',
                col_map['Tiền và các khoản tương đương tiền'],
                col_map['Các khoản đầu tư tài chính ngắn hạn'],
                col_map['Các khoản phải thu ngắn hạn'],
                col_map['Hàng tồn kho'],
                col_map['Tài sản ngắn hạn khác'],
                col_map['Các khoản phải thu dài hạn'],
                col_map['Tài sản cố định'],
                col_map['Tài sản dở dang dài hạn'],
                col_map['Bất động sản đầu tư'],
                col_map['Đầu tư tài chính dài hạn'],
                col_map['Tài sản dài hạn khác'],
                col_map['Nợ ngắn hạn'],
                col_map['Nợ dài hạn'],
                col_map['Vốn chủ sở hữu'],
                col_map['Nguồn kinh phí và quỹ khác'],
            ]
            row_data = [row.get('Quý', ''), row.get('Năm', '')] + [row.get(c, '') for c in keep_cols[2:]]
            # Thêm các chỉ số tài chính
            row_data += [
                debt_ratio, de_ratio, asset_leverage, equity_to_asset,
                long_debt_to_equity, financial_leverage, current_ratio, quick_ratio
            ]
            result.append(row_data)
        except Exception as e:
            print(f"Lỗi xử lý dòng {idx}: {e}")

    # Tạo DataFrame kết quả
    out_cols = [
        'Quý', 'Năm', 'Tiền và các khoản tương đương tiền', 'Các khoản đầu tư tài chính ngắn hạn',
        'Các khoản phải thu ngắn hạn', 'Hàng tồn kho', 'Tài sản ngắn hạn khác',
        'Các khoản phải thu dài hạn', 'Tài sản cố định', 'Tài sản dở dang dài hạn',
        'Bất động sản đầu tư', 'Đầu tư tài chính dài hạn', 'Tài sản dài hạn khác',
        'Nợ ngắn hạn', 'Nợ dài hạn', 'Vốn chủ sở hữu', 'Nguồn kinh phí và quỹ khác',
        'Debt Ratio', 'D/E', 'Asset Leverage', 'Equity/Asset',
        'Long Debt/Equity', 'Financial Leverage', 'Current Ratio', 'Quick Ratio'
    ]
    df_out = pd.DataFrame(result, columns=out_cols)

    # Lưu file kết quả với encoding utf-8-sig để không lỗi tiếng Việt
    out_dir = os.path.abspath(os.path.join(output_dir, '../../load/csv'))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{IDcp}_balance_sheet_processed.csv")
    df_out.to_csv(out_path, index=False, encoding='utf-8-sig')

    # Lưu lại file gốc (nếu muốn backup)
    # df.to_csv(os.path.join(out_dir, f"{IDcp}_balance_sheet_backup.csv"), index=False, encoding='utf-8-sig')

    print(f"Đã lưu file kết quả: {out_path}")
    return True