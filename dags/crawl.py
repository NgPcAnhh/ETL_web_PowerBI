import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Config:
    """Configuration class containing all constants and field definitions"""
    
    # Constants
    STOCK_CODE = "VGI"
    START_YEAR = 2008
    END_YEAR = 2030
    QUARTER_COUNT = 4
    
    # Report types
    BALANCE_SHEET = "bsheet"
    INCOME_STATEMENT = "incsta"
    CASH_FLOW = "cashflow"
    CASH_FLOW_DIRECT = "cashflowdirect"
    
    REPORT_TYPES = [BALANCE_SHEET, INCOME_STATEMENT, CASH_FLOW]
    
    REPORT_TYPE_TO_SHEET = {
        BALANCE_SHEET: "Balance Sheet",
        INCOME_STATEMENT: "Income Statement",
        CASH_FLOW: "Cash Flow",
        CASH_FLOW_DIRECT: "Cash Flow Direct",
    }
    
    # Balance Sheet Fields
    BALANCE_SHEET_FIELDS = [
        "TÀI SẢN",
        "A- TÀI SẢN NGẮN HẠN",
        "I. Tiền và các khoản tương đương tiền",
        "1. Tiền",
        "2. Các khoản tương đương tiền",
        "II. Các khoản đầu tư tài chính ngắn hạn",
        "1. Chứng khoán kinh doanh",
        "2. Dự phòng giảm giá chứng khoán kinh doanh",
        "3. Đầu tư nắm giữ đến ngày đáo hạn",
        "III. Các khoản phải thu ngắn hạn",
        "1. Phải thu ngắn hạn của khách hàng",
        "2. Trả trước cho người bán ngắn hạn",
        "3. Phải thu nội bộ ngắn hạn",
        "4. Phải thu theo tiến độ kế hoạch hợp đồng xây dựng",
        "5. Phải thu về cho vay ngắn hạn",
        "6. Phải thu ngắn hạn khác",
        "7. Dự phòng phải thu ngắn hạn khó đòi",
        "8. Tài sản Thiếu chờ xử lý",
        "IV. Hàng tồn kho",
        "1. Hàng tồn kho",
        "2. Dự phòng giảm giá hàng tồn kho",
        "V.Tài sản ngắn hạn khác",
        "1. Chi phí trả trước ngắn hạn",
        "2. Thuế GTGT được khấu trừ",
        "3. Thuế và các khoản khác phải thu Nhà nước",
        "4. Giao dịch mua bán lại trái phiếu Chính phủ",
        "5. Tài sản ngắn hạn khác",
        "B. TÀI SẢN DÀI HẠN",
        "I. Các khoản phải thu dài hạn",
        "1. Phải thu dài hạn của khách hàng",
        "2. Trả trước cho người bán dài hạn",
        "3. Vốn kinh doanh ở đơn vị trực thuộc",
        "4. Phải thu nội bộ dài hạn",
        "5. Phải thu về cho vay dài hạn",
        "6. Phải thu dài hạn khác",
        "7. Dự phòng phải thu dài hạn khó đòi",
        "II.Tài sản cố định",
        "1. Tài sản cố định hữu hình",
        "- Nguyên giá",
        "- Giá trị hao mòn lũy kế",
        "2. Tài sản cố định thuê tài chính",
        "- Nguyên giá",
        "- Giá trị hao mòn lũy kế",
        "3. Tài sản cố định vô hình",
        "- Nguyên giá",
        "- Giá trị hao mòn lũy kế",
        "III. Bất động sản đầu tư",
        "- Nguyên giá",
        "- Giá trị hao mòn lũy kế",
        "IV. Tài sản dở dang dài hạn",
        "1. Chi phí sản xuất, kinh doanh dở dang dài hạn",
        "2. Chi phí xây dựng cơ bản dở dang",
        "V. Đầu tư tài chính dài hạn",
        "1. Đầu tư vào công ty con",
        "2. Đầu tư vào công ty liên kết, liên doanh",
        "3. Đầu tư góp vốn vào đơn vị khác",
        "4. Dự phòng đầu tư tài chính dài hạn",
        "5. Đầu tư nắm giữ đến ngày đáo hạn",
        "VI. Tài sản dài hạn khác",
        "1. Chi phí trả trước dài hạn",
        "2. Tài sản thuế thu nhập hoãn lại",
        "3. Thiết bị, vật tư, phụ tùng thay thế dài hạn",
        "4. Tài sản dài hạn khác",
        "5. Lợi thế thương mại",
        "TỔNG CỘNG TÀI SẢN",
        "NGUỒN VỐN",
        "C. NỢ PHẢI TRẢ",
        "I. Nợ ngắn hạn",
        "1. Phải trả người bán ngắn hạn",
        "2. Người mua trả tiền trước ngắn hạn",
        "3. Thuế và các khoản phải nộp nhà nước",
        "4. Phải trả người lao động",
        "5. Chi phí phải trả ngắn hạn",
        "6. Phải trả nội bộ ngắn hạn",
        "7. Phải trả theo tiến độ kế hoạch hợp đồng xây dựng",
        "8. Doanh thu chưa thực hiện ngắn hạn",
        "9. Phải trả ngắn hạn khác",
        "10. Vay và nợ thuê tài chính ngắn hạn",
        "11. Dự phòng phải trả ngắn hạn",
        "12. Quỹ khen thưởng phúc lợi",
        "13. Quỹ bình ổn giá",
        "14. Giao dịch mua bán lại trái phiếu Chính phủ",
        "II. Nợ dài hạn",
        "1. Phải trả người bán dài hạn",
        "2. Người mua trả tiền trước dài hạn",
        "3. Chi phí phải trả dài hạn",
        "4. Phải trả nội bộ về vốn kinh doanh",
        "5. Phải trả nội bộ dài hạn",
        "6. Doanh thu chưa thực hiện dài hạn",
        "7. Phải trả dài hạn khác",
        "8. Vay và nợ thuê tài chính dài hạn",
        "9. Trái phiếu chuyển đổi",
        "10. Cổ phiếu ưu đãi",
        "11. Thuế thu nhập hoãn lại phải trả",
        "12. Dự phòng phải trả dài hạn",
        "13. Quỹ phát triển khoa học và công nghệ",
        "D.VỐN CHỦ SỞ HỮU",
        "I. Vốn chủ sở hữu",
        "1. Vốn góp của chủ sở hữu",
        "- Cổ phiếu phổ thông có quyền biểu quyết",
        "- Cổ phiếu ưu đãi",
        "2. Thặng dư vốn cổ phần",
        "3. Quyền chọn chuyển đổi trái phiếu",
        "4. Vốn khác của chủ sở hữu",
        "5. Cổ phiếu quỹ",
        "6. Chênh lệch đánh giá lại tài sản",
        "7. Chênh lệch tỷ giá hối đoái",
        "8. Quỹ đầu tư phát triển",
        "9. Quỹ hỗ trợ sắp xếp doanh nghiệp",
        "10. Quỹ khác thuộc vốn chủ sở hữu",
        "11. Lợi nhuận sau thuế chưa phân phối",
        "- LNST chưa phân phối lũy kế đến cuối kỳ trước",
        "- LNST chưa phân phối kỳ này",
        "12. Nguồn vốn đầu tư XDCB",
        "13. Lợi ích cổ đông không kiểm soát",
        "II. Nguồn kinh phí và quỹ khác",
        "1. Nguồn kinh phí",
        "2. Nguồn kinh phí đã hình thành TSCĐ",
        "TỔNG CỘNG NGUỒN VỐN",
    ]
    
    # Income Statement Fields
    INCOME_STATEMENT_FIELDS = [
        "Doanh thu bán hàng và cung cấp dịch vụ",
        "2. Các khoản giảm trừ doanh thu",
        "3. Doanh thu thuần về bán hàng và cung cấp dịch vụ (10 = 01 - 02)",
        "4. Giá vốn hàng bán",
        "5. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ(20=10-11)",
        "6. Doanh thu hoạt động tài chính",
        "7. Chi phí tài chính",
        "- Trong đó: Chi phí lãi vay",
        "8. Phần lãi lỗ trong công ty liên doanh, liên kết",
        "9. Chi phí bán hàng",
        "10. Chi phí quản lý doanh nghiệp",
        "11. Lợi nhuận thuần từ hoạt động kinh doanh{30=20+(21-22) + 24 - (25+26)}",
        "12. Thu nhập khác",
        "13. Chi phí khác",
        "14. Lợi nhuận khác(40=31-32)",
        "15. Tổng lợi nhuận kế toán trước thuế(50=30+40)",
        "16. Chi phí thuế TNDN hiện hành",
        "17. Chi phí thuế TNDN hoãn lại",
        "18. Lợi nhuận sau thuế thu nhập doanh nghiệp(60=50-51-52)",
        "19. Lợi nhuận sau thuế công ty mẹ",
        "20. Lợi nhuận sau thuế công ty mẹ không kiểm soát",
        "21. Lãi cơ bản trên cổ phiếu()",
        "22. Lãi suy giảm trên cổ phiếu ()",
    ]
    
    # Cash Flow Fields
    CASH_FLOW_FIELDS = [
        "I. Lưu chuyển tiền từ hoạt động kinh doanh",
        "1. Lợi nhuận trước thuế",
        "2. Điều chỉnh cho các khoản",
        "- Khấu hao TSCĐ và BĐSĐT",
        "- Các khoản dự phòng",
        "- Lãi, lỗ chênh lệch tỷ giá hối đoái do đánh giá lại các khoản mục tiền tệ có gốc ngoại tệ",
        "- Lãi, lỗ từ hoạt động đầu tư",
        "- Chi phí lãi vay",
        "- Các khoản điều chỉnh khác",
        "3. Lợi nhuận từ hoạt động kinh doanh trước thay đổi vốn lưu động",
        "- Tăng, giảm các khoản phải thu",
        "- Tăng, giảm hàng tồn kho",
        "- Tăng, giảm các khoản phải trả (Không kể lãi vay phải trả, thuế thu nhập doanh nghiệp phải nộp)",
        "- Tăng, giảm chi phí trả trước",
        "- Tăng, giảm chứng khoán kinh doanh",
        "- Tiền lãi vay đã trả",
        "- Thuế thu nhập doanh nghiệp đã nộp",
        "- Tiền thu khác từ hoạt động kinh doanh",
        "- Tiền chi khác cho hoạt động kinh doanh",
        "Lưu chuyển tiền thuần từ hoạt động kinh doanh",
        "II. Lưu chuyển tiền từ hoạt động đầu tư",
        "1.Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác",
        "2.Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác",
        "3.Tiền chi cho vay, mua các công cụ nợ của đơn vị khác",
        "4.Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác",
        "5.Tiền chi đầu tư góp vốn vào đơn vị khác",
        "6.Tiền thu hồi đầu tư góp vốn vào đơn vị khác",
        "7.Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia",
        "Lưu chuyển tiền thuần từ hoạt động đầu tư",
        "III. Lưu chuyển tiền từ hoạt động tài chính",
        "1.Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu",
        "2.Tiền trả lại vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành",
        "3.Tiền thu từ đi vay",
        "4.Tiền chi trả nợ gốc vay",
        "5.Tiền chi trả nợ gốc thuê tài chính",
        "6. Cổ tức, lợi nhuận đã trả cho chủ sở hữu",
        "7. Tiền thu từ vốn góp của cổ đông không kiểm soát",
        "Lưu chuyển tiền thuần từ hoạt động tài chính",
        "Lưu chuyển tiền thuần trong kỳ (50 = 20+30+40)",
        "Tiền và tương đương tiền đầu kỳ",
        "Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ",
        "Tiền và tương đương tiền cuối kỳ",
    ]
    
    @staticmethod
    def build_url(stock_code, report_type, year):
        """Build URL for fetching financial statements"""
        return f"https://cafef.vn/du-lieu/bao-cao-tai-chinh/{stock_code}/{report_type}/{year}/4/0/0/bao-cao-tai-chinh-.chn"


class FinancialDataCrawler:
    """Class for crawling financial data from CafeF"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def crawl_report(self, stock_code, report_type, year):
        """Fetch financial report data from CafeF"""
        url = Config.build_url(stock_code, report_type, year)
        
        # Add random sleep between 2-4 seconds to avoid overloading the server
        sleep_time = random.uniform(2, 4)
        logging.info(f"Waiting {sleep_time:.2f} seconds before fetching {report_type} for year {year}")
        time.sleep(sleep_time)
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return self._parse_report_html(response.text)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch URL {url}: {str(e)}")
    
    def _parse_report_html(self, html_content):
        """Extract financial data from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the table with financial data
        table = soup.find('table', id='tableContent')
        if not table:
            raise Exception("Table with ID 'tableContent' not found")
        
        rows = []
        
        # Process each row
        for tr in table.find_all('tr', class_=['r_item', 'r_item_a']):
            row = []
            
            # Get all cells in the row
            cells = tr.find_all('td', class_='b_r_c')
            
            if cells:
                # Get the description (first column)
                description = cells[0].get_text(strip=True)
                row.append(description)
                
                # Get the quarterly data (next 4 columns)
                for cell in cells[1:]:
                    value = cell.get_text(strip=True)
                    row.append(value)
                
                # Add the row if it has data
                if len(row) > 0:
                    rows.append(row)
        
        return rows


class ExcelWriter:
    """Class for writing data to Excel files"""
    
    @staticmethod
    def write_to_excel(output_path, data):
        """Write financial data to Excel file"""
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, sheet_data in data.items():
                if sheet_data:
                    # Convert to DataFrame
                    df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
                    
                    # Write to Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logging.info(f"Data exported to: {output_path}")


def main():
    """Main function to orchestrate the data extraction process"""
    
    # Initialize crawler and writer
    crawler = FinancialDataCrawler()
    excel_writer = ExcelWriter()
    
    # Add "Quý" as the first field in each sheet's headers
    balance_sheet_headers = ["Quý"] + Config.BALANCE_SHEET_FIELDS
    income_statement_headers = ["Quý"] + Config.INCOME_STATEMENT_FIELDS
    cash_flow_headers = ["Quý"] + Config.CASH_FLOW_FIELDS
    
    # Initialize data with modified headers
    all_data = {
        Config.REPORT_TYPE_TO_SHEET[Config.BALANCE_SHEET]: [balance_sheet_headers],
        Config.REPORT_TYPE_TO_SHEET[Config.INCOME_STATEMENT]: [income_statement_headers],
        Config.REPORT_TYPE_TO_SHEET[Config.CASH_FLOW]: [cash_flow_headers],
    }
    
    # Track progress
    total_requests = (Config.END_YEAR - Config.START_YEAR + 1) * len(Config.REPORT_TYPES)
    current_request = 0
    
    # Fetch data for each year and report type
    for year in range(Config.START_YEAR, Config.END_YEAR + 1):
        for report in Config.REPORT_TYPES:
            current_request += 1
            print(f"[{current_request}/{total_requests}] Fetching {report} for year {year}")
            
            try:
                rows = crawler.crawl_report(Config.STOCK_CODE, report, year)
                
                # Each row is a slice: [description, Q1, Q2, Q3, Q4]
                # We want to build 4 rows per year, one for each quarter
                for q in range(Config.QUARTER_COUNT):
                    quarter = f"{q+1}/{year}"
                    data_row = [quarter]
                    
                    # Add each field's value for this quarter
                    for row in rows:
                        if len(row) > q + 1:
                            data_row.append(row[q + 1])
                        else:
                            data_row.append("")
                    
                    all_data[Config.REPORT_TYPE_TO_SHEET[report]].append(data_row)
                    
            except Exception as e:
                logging.error(f"Error fetching {report} {year}: {e}")
                continue
    
    # Create output path with fixed directory
    output_path = r"opt/airflow/data_crawl/financial_report_{}.xlsx".format(Config.STOCK_CODE)
    
    # Write to Excel
    try:
        excel_writer.write_to_excel(output_path, all_data)
        print(f"Data exported to: {output_path}")
    except Exception as e:
        logging.error(f"Failed to write Excel: {e}")


if __name__ == "__main__":
    main()