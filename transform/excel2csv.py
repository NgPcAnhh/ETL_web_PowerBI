import pandas as pd
import os
import sys
import re

def excel2csv_from_config(config_path):
    # Đọc config
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        return False

    excel_path = None
    output_dir = None
    ma_cp = None

    # Đọc các biến từ config
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                if key == 'excel_path':
                    excel_path = value
                elif key == 'output_dir':
                    output_dir = value
                elif key in ['ma_cp', 'IDcp']:
                    ma_cp = value

    # Thay thế biến {ma_cp} trong excel_path nếu có
    if excel_path and '{ma_cp}' in excel_path and ma_cp:
        excel_path = excel_path.replace('{ma_cp}', ma_cp)

    if not excel_path:
        print("Error: Excel path not found in config file")
        return False
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(excel_path), "csv_output")

    print(f"Converting Excel file: {excel_path}")
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found at {excel_path}")
        return False
    os.makedirs(output_dir, exist_ok=True)
    try:
        excel = pd.ExcelFile(excel_path)
        filename = os.path.basename(excel_path)
        if ma_cp:
            stock_code = ma_cp
        elif '_' in filename:
            stock_code = filename.split('_')[-1].split('.')[0]
        else:
            stock_code = filename.split('.')[0]
        for sheet_name in excel.sheet_names:
            print(f"Processing sheet: {sheet_name}")
            df = pd.read_excel(excel, sheet_name, dtype=str, keep_default_na=False)
            df = df.astype(str)
            # Đảm bảo tên cột không bắt đầu bằng "=" hoặc "-"
            df.columns = [re.sub(r'^[=\-]+', '', col) if isinstance(col, str) else col for col in df.columns]
            # Đảm bảo các giá trị dòng đầu tiên không bắt đầu bằng "=" hoặc "-"
            df.iloc[0] = df.iloc[0].apply(lambda x: x.lstrip("=-") if isinstance(x, str) else x)
            df = df.applymap(lambda x: "'" + x if isinstance(x, str) and x.startswith('=') else x)
            # Nếu muốn giữ xử lý cột Quý như trước:
            if 'Quý' in df.columns:
                df['Quý'] = df['Quý'].apply(lambda x: "'" + x if not x.startswith("'") else x)
            safe_sheet_name = sheet_name.replace(' ', '_').lower()
            csv_filename = f"{stock_code}_{safe_sheet_name}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"Created CSV file: {csv_path}")
        print("Conversion completed successfully!")
        return True
    except Exception as e:
        print(f"Error converting Excel to CSV: {str(e)}")
        return False