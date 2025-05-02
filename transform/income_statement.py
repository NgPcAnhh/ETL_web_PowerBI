import pandas as pd
import os
import re

def process_income_statement_from_config(config_path):
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
    input_path = os.path.normpath(os.path.join(input_dir, f"{ma_cp}_income_statement.csv"))
    output_dir = os.path.normpath(os.path.join("../load/csv"))
    output_path = os.path.normpath(os.path.join(output_dir, f"{ma_cp}_income_statement.csv"))
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

    # Đưa 2 cột Quý, Năm lên đầu, giữ nguyên các cột còn lại
    cols = df.columns.tolist()
    if 'Quý' in cols and 'Năm' in cols:
        cols.remove('Quý')
        cols.remove('Năm')
        cols = ['Quý', 'Năm'] + cols
    df = df[cols]

    # Làm sạch dữ liệu số cho tất cả các cột trừ 'Quý' và 'Năm'
    def clean_number(x):
        s = str(x).replace(',', '').replace(' ', '')
        if s == '' or s.lower() == 'nan':
            return ''
        try:
            return float(s)
        except:
            return x  # Giữ nguyên nếu không phải số

    for col in df.columns:
        if col not in ['Quý', 'Năm']:
            df[col] = df[col].apply(clean_number)

    df['Quý'] = df['Quý'].astype(str)
    df['Năm'] = df['Năm'].astype(str)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Đã lưu file kết quả: {output_path}")
    return True