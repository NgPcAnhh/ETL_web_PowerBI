import pandas as pd
import os
import re
from time import sleep

class Config:
    """Class để đọc và quản lý config"""
    
    def __init__(self, config_path="config.txt"):
        self.config = {}
        self.load_config(config_path)
    
    def load_config(self, config_path):
        """Đọc config từ file"""
        if not os.path.exists(config_path):
            # Tạo config mặc định nếu không tồn tại
            self.config = {
                'ma_cp': 'VGI',
                'excel_path': r'opt/airflow/data_crawl/financial_report_{ma_cp}.xlsx',
                'output_dir': r'opt/airflow/load/csv',
                'start': '1/2008',
                'end': '4/2024'
            }
            print(f"Sử dụng config mặc định vì không tìm thấy file {config_path}")
            return
        
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                self.config[key.strip()] = value.strip().strip('"\'')
    
    def get(self, key, default=''):
        """Lấy giá trị config"""
        return self.config.get(key, default)


class ExcelToCSVConverter:
    """Class chuyển đổi Excel sang CSV"""
    
    def __init__(self, config):
        self.config = config
    
    def convert(self):
        """Chuyển đổi Excel sang CSV"""
        ma_cp = self.config.get('ma_cp') or self.config.get('IDcp', '')
        excel_path = self.config.get('excel_path', '')
        output_dir = self.config.get('output_dir', '')
        
        # Thay thế biến {ma_cp} trong excel_path nếu có
        if excel_path and '{ma_cp}' in excel_path and ma_cp:
            excel_path = excel_path.replace('{ma_cp}', ma_cp)
        
        if not excel_path:
            print("Error: Excel path not found in config")
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
                
                # Xử lý cột Quý
                if 'Quý' in df.columns:
                    df['Quý'] = df['Quý'].apply(lambda x: "'" + x if not x.startswith("'") else x)
                
                safe_sheet_name = sheet_name.replace(' ', '_').lower()
                csv_filename = f"{stock_code}_{safe_sheet_name}.csv"
                csv_path = os.path.join(output_dir, csv_filename)
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f"Created CSV file: {csv_path}")
            
            print("Excel to CSV conversion completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error converting Excel to CSV: {str(e)}")
            return False


class BalanceSheetProcessor:
    """Class xử lý Balance Sheet"""
    
    def __init__(self, config):
        self.config = config
    
    def process(self):
        """Xử lý Balance Sheet"""
        ma_cp = self.config.get('ma_cp') or self.config.get('IDcp', '')
        input_dir = self.config.get('output_dir', '')
        start = self.config.get('start', '')
        end = self.config.get('end', '')
        
        input_path = os.path.join(input_dir, f"{ma_cp}_balance_sheet.csv")
        output_dir = r"opt/airflow/load/csv"
        output_path = os.path.join(output_dir, f"{ma_cp}_balance_sheet.csv")
        os.makedirs(output_dir, exist_ok=True)
        
        if not os.path.exists(input_path):
            print(f"Không tìm thấy file: {input_path}")
            return False
        
        # Đọc dữ liệu
        df = pd.read_csv(input_path, dtype={'Quý': str})
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
        
        # Mapping cột
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
        
        # Lưu file kết quả
        df_out.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Đã lưu file Balance Sheet: {output_path}")
        return True


class IncomeStatementProcessor:
    """Class xử lý Income Statement"""
    
    def __init__(self, config):
        self.config = config
    
    def process(self):
        """Xử lý Income Statement"""
        ma_cp = self.config.get('ma_cp') or self.config.get('IDcp', '')
        input_dir = self.config.get('output_dir', '')
        
        input_path = os.path.join(input_dir, f"{ma_cp}_income_statement.csv")
        output_dir = r"opt/airflow/load/csv"
        output_path = os.path.join(output_dir, f"{ma_cp}_income_statement.csv")
        os.makedirs(output_dir, exist_ok=True)
        
        if not os.path.exists(input_path):
            print(f"Không tìm thấy file: {input_path}")
            return False
        
        # Đọc dữ liệu
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
        
        # Làm sạch dữ liệu số
        def clean_number(x):
            s = str(x).replace(',', '').replace(' ', '')
            if s == '' or s.lower() == 'nan':
                return ''
            try:
                return float(s)
            except:
                return x
        
        for col in df.columns:
            if col not in ['Quý', 'Năm']:
                df[col] = df[col].apply(clean_number)
        
        df['Quý'] = df['Quý'].astype(str)
        df['Năm'] = df['Năm'].astype(str)
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Đã lưu file Income Statement: {output_path}")
        return True


class CashFlowProcessor:
    """Class xử lý Cash Flow"""
    
    def __init__(self, config):
        self.config = config
    
    def process(self):
        """Xử lý Cash Flow"""
        ma_cp = self.config.get('ma_cp') or self.config.get('IDcp', '')
        input_dir = self.config.get('output_dir', '')
        
        input_path = os.path.join(input_dir, f"{ma_cp}_cash_flow.csv")
        output_dir = r"opt/airflow/load/csv"
        output_path = os.path.join(output_dir, f"{ma_cp}_cash_flow.csv")
        os.makedirs(output_dir, exist_ok=True)
        
        if not os.path.exists(input_path):
            print(f"Không tìm thấy file: {input_path}")
            return False
        
        # Đọc dữ liệu
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
        print(f"Đã lưu file Cash Flow: {output_path}")
        return True


def main():
    """Hàm main thực hiện toàn bộ quá trình transform"""
    
    print("=== BẮT ĐẦU QUÁ TRÌNH TRANSFORM DỮ LIỆU ===")
    
    # Đọc config (có thể tạo file config.txt hoặc sử dụng config mặc định)
    config = Config("config.txt")
    
    # Bước 1: Chuyển đổi Excel sang CSV
    print("\n1. Chuyển đổi Excel sang CSV...")
    excel_converter = ExcelToCSVConverter(config)
    if not excel_converter.convert():
        print("Lỗi khi chuyển đổi Excel sang CSV")
        return False
    
    sleep(0.5)
    
    # Bước 2: Xử lý Balance Sheet
    print("\n2. Xử lý Balance Sheet...")
    balance_processor = BalanceSheetProcessor(config)
    if not balance_processor.process():
        print("Lỗi khi xử lý Balance Sheet")
    
    sleep(0.5)
    
    # Bước 3: Xử lý Income Statement
    print("\n3. Xử lý Income Statement...")
    income_processor = IncomeStatementProcessor(config)
    if not income_processor.process():
        print("Lỗi khi xử lý Income Statement")
    
    sleep(0.5)
    
    # Bước 4: Xử lý Cash Flow
    print("\n4. Xử lý Cash Flow...")
    cashflow_processor = CashFlowProcessor(config)
    if not cashflow_processor.process():
        print("Lỗi khi xử lý Cash Flow")
    
    print("\n=== HOÀN THÀNH QUÁ TRÌNH TRANSFORM ===")
    print(f"Các file đã được lưu vào: D:\\Users\\ADMIN\\OneDrive\\Máy tính\\New folder\\ETL_web_PowerBI\\load\\csv")


if __name__ == "__main__":
    main()