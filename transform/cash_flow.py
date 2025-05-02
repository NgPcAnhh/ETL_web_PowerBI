import pandas as pd
import os
import re

def process_cash_flow_from_config(config_path):
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
    ma_cp = config.get('ma_cp', '') or config.get('IDcp', '')
    input_dir = config.get('output_dir', '../csv/data_processed')
    input_path = os.path.normpath(os.path.join(input_dir, f"{ma_cp}_cash_flow.csv"))
    output_dir = os.path.normpath(os.path.join("../load/csv"))
    output_path = os.path.normpath(os.path.join(output_dir, f"{ma_cp}_cash_flow.csv"))
    os.makedirs(output_dir, exist_ok=True)

    # Đọc dữ liệu, đảm bảo cột Quý là text
    df = pd.read_csv(input_path, dtype={'Quý': str})
    df = df.fillna('')

    # Tách cột Quý thành 2 cột: Quý và Năm
    def split_quarter(q):
        m = re.match(r"'?(\d+)/(\d+)", str(q))
        if m:
            return m.group(1), m.group(2)
        return '', ''
    df[['Quý', 'Năm']] = df['Quý'].apply(split_quarter).apply(pd.Series)

    # Đưa 2 cột Quý, Năm lên đầu
    cols = df.columns.tolist()
    if 'Quý' in cols and 'Năm' in cols:
        cols.remove('Quý')
        cols.remove('Năm')
        cols = ['Quý', 'Năm'] + cols
    df = df[cols]

    # Xóa 3 cột nếu tồn tại
    cols_to_drop = [
        'I. Lưu chuyển tiền từ hoạt động kinh doanh',
        'II. Lưu chuyển tiền từ hoạt động đầu tư',
        'III. Lưu chuyển tiền từ hoạt động tài chính'
    ]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')

    # Tính toán các chỉ số
    # Tên cột có thể khác nhau, cần dò tìm tên gần đúng
    def find_col(possibles, columns):
        for p in possibles:
            for c in columns:
                if p.lower() in c.lower():
                    return c
        return None

    col_lctt_hdkd = find_col(['Lưu chuyển tiền thuần từ hoạt động kinh doanh'], df.columns)
    col_lntt = find_col(['Lợi nhuận trước thuế'], df.columns)
    col_lai_vay = find_col(['Chi phí lãi vay', 'lãi vay'], df.columns)

    def to_num(x):
        s = str(x).replace(',', '').replace(' ', '')
        if s == '' or s.lower() == 'nan':
            return None
        try:
            return float(s)
        except:
            return None

    # Tính chỉ số tạo tiền và tỷ lệ chi trả lãi vay
    chi_so_tao_tien = []
    ty_le_chi_tra_lai_vay = []
    for idx, row in df.iterrows():
        lctt = to_num(row[col_lctt_hdkd]) if col_lctt_hdkd else None
        lntt = to_num(row[col_lntt]) if col_lntt else None
        lai_vay = to_num(row[col_lai_vay]) if col_lai_vay else None
        # Chỉ số tạo tiền
        if lctt is not None and lntt not in (None, 0):
            chi_so = lctt / lntt
        else:
            chi_so = ''
        # Tỷ lệ chi trả lãi vay
        if lctt is not None and lai_vay not in (None, 0):
            ty_le = lctt / lai_vay
        else:
            ty_le = ''
        chi_so_tao_tien.append(chi_so)
        ty_le_chi_tra_lai_vay.append(ty_le)

    df['Chỉ số tạo tiền'] = chi_so_tao_tien
    df['Tỷ lệ chi trả lãi vay'] = ty_le_chi_tra_lai_vay

    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Đã lưu file kết quả: {output_path}")
    return True