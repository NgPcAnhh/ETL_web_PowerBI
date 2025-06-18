""" import các thư viện sử dụng """
from flask import Flask, render_template, session, request, jsonify
import os
from datetime import datetime, timedelta
import re
import subprocess
from database.user_queries import execute_query  # để thực hiện được query trong sql


""" Khai báo các biến toàn cục """
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set the secret key to a random 24-byte string
app.permanent_session_lifetime = timedelta(minutes=30)  # Server-side fallback timeout


""" Khai báo route """
@app.route('/')
def index():
    session.permanent = True
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/freereport')
def freereport():
    return render_template('freereport.html')

@app.route('/premiumreport')
def premiumreport():
    return render_template('premiumreport.html')

@app.route('/purchase')
def purchase():
    return render_template('purchase.html')


# @app.route('/logout')
# def logout():
#     session.clear()
#     return render_template('logout.html')

@app.route('/admin')
def admin():
    session.permanent = True
    return render_template('admin.html')


""" Xử lý logic """

def get_user_by_login_name(login_name):
    query = "SELECT status, idusers, username, password FROM users WHERE username = %s"
    result = execute_query(query, (login_name,))
    return result


# xử lý đăng nhập và khởi tạo session
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    user = get_user_by_login_name(username)
    
    if user and user[0]['password'] == password:
        # Login successful
        session['user_id'] = user[0]['idusers']
        session['username'] = username
        session['status'] = user[0]['status']
        session.permanent = True  # Make the session permanent
        return jsonify({'success': True, 'message': 'Login successful', 'status': user[0]['status']}), 200    
    else:
        # Login failed
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401


# xử lý logout
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


# xử lý thông tin đẩy lên main.html
@app.route('/api/userinfo')
def api_userinfo():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    query = "SELECT username, idusers, status FROM users WHERE idusers = %s"
    result = execute_query(query, (user_id,))
    if not result:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(result[0])


# xử lý đăng kí tài khoản
def create_user(username, password):
    # Kiểm tra username đã tồn tại chưa
    query_check = "SELECT idusers FROM users WHERE username = %s"
    if execute_query(query_check, (username,)):
        return False, "Username already exists"
    # Thêm user mới chỉ với username và password
    query_insert = "INSERT INTO users (username, password) VALUES (%s, %s)"
    execute_query(query_insert, (username, password))
    return True, "Register successful"


@app.route('/register', methods=['POST'])
def register_post():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    # Kiểm tra username đã tồn tại chưa
    query_check = "SELECT idusers FROM users WHERE username = %s"
    result = execute_query(query_check, (username,))
    if result and len(result) > 0:
        return jsonify({'success': False, 'message': 'Username already exists'}), 409

    # Thêm user mới
    query_insert = "INSERT INTO users (username, password) VALUES (%s, %s)"
    insert_result = execute_query(query_insert, (username, password))
    if insert_result:
        return jsonify({'success': True, 'message': 'Register successful'}), 200
    else:
        return jsonify({'success': False, 'message': 'Database error'}), 500


@app.route('/api/submit-requirement', methods=['POST'])
def submit_requirement():
    try:
        data = request.get_json()
        gmail = data.get('gmail')
        discussion = data.get('discussion')
        time = data.get('time')
        user_id = session.get('user_id')

        if not user_id:
            return jsonify({'error': 'Not logged in'}), 401
        if not gmail or not discussion or not time:
            return jsonify({'error': 'Missing fields'}), 400

        # Xử lý thời gian: loại bỏ 'Z' nếu có
        if time.endswith('Z'):
            time = time[:-1]
        # Nếu có dấu chấm (microseconds), cắt về định dạng DATETIME MySQL
        if '.' in time:
            time = time.split('.')[0]

        # Lưu vào database bằng hàm execute_query
        query = "INSERT INTO requirements (id, gmail, discussion, time) VALUES (%s, %s, %s, %s)"
        result = execute_query(query, (user_id, gmail, discussion, time))
        if result is None:
            return jsonify({'error': 'Database error'}), 500

        return jsonify({'success': True, 'message': 'Requirement submitted successfully'}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500
    


# xử lý admin sql
@app.route('/exec-sql', methods=['POST'])
def admin_exec_sql():
    data = request.get_json()
    sql = data.get('sql', '').strip()
    
    print(f"Received SQL query: {sql}")  # Debug để kiểm tra
    
    if not sql:
        return jsonify({'error': 'No SQL provided'}), 400

    try:
        if sql.strip().lower().startswith('select'):
            result = execute_query(sql, ())
            return jsonify({'result': result}), 200
        else:
            affected = execute_query(sql, ())
            return jsonify({'result': [{'affected_rows': affected}]}), 200
    except Exception as e:
        print(f"SQL Error: {str(e)}")  # Debug để kiểm tra lỗi
        return jsonify({'error': str(e)}), 400


# xử lý logout 
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.method == 'POST':
        # Return JSON response for AJAX requests from admin.js
        return jsonify({'success': True}), 200
    else:
        # Return HTML template for normal browser navigation
        return render_template('logout.html')


# xử lý admin crawl command
@app.route('/admin-crawl', methods=['POST'])
def admin_crawl():
    # Initialize variables for error recovery
    config_path = None
    original_content = None
    
    try:
        print("Received admin-crawl request")
        
        # Parse the request data
        data = request.get_json()
        if not data:
            print("Error: No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
            
        command = data.get('command', '').strip()
        print(f"Command received: {command}")
        
        # Debug session information
        print(f"Session data: {session}")
        print(f"User ID from session: {session.get('user_id')}")
        
        # Parse the command to get the stock code
        if not command.startswith('crawl '):
            print("Error: Invalid command format")
            return jsonify({'error': 'Command must start with "crawl"'}), 400
            
        parts = command.split(' ', 1)
        if len(parts) < 2:
            print("Error: Missing parameter")
            return jsonify({'error': 'Missing stock code parameter'}), 400
            
        param = parts[1].strip()
        if len(param) != 3:
            print(f"Error: Parameter '{param}' must be exactly 3 characters")
            return jsonify({'error': 'Stock code must be exactly 3 characters'}), 400
        
        print(f"Processing crawl for stock code: {param}")
        
        # Get absolute paths for better reliability
        app_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(app_dir)
        extract_dir = os.path.join(project_dir, 'extract')
        config_dir = os.path.join(extract_dir, 'config')
        config_path = os.path.join(config_dir, 'config.go')
        main_go_path = os.path.join(extract_dir, 'main.go')
        
        # Debug path information
        print(f"Working directory: {os.getcwd()}")
        print(f"App directory: {app_dir}")
        print(f"Project directory: {project_dir}")
        print(f"Extract directory: {extract_dir}")
        print(f"Config directory: {config_dir}")
        print(f"Config file path: {config_path}")
        print(f"Main.go path: {main_go_path}")
        
        # Check if the necessary files exist
        if not os.path.exists(config_path):
            print(f"Error: Config file not found at {config_path}")
            return jsonify({'error': f'Config file not found at {config_path}'}), 500
            
        if not os.path.exists(main_go_path):
            print(f"Error: Main.go file not found at {main_go_path}")
            return jsonify({'error': f'Main.go file not found at {main_go_path}'}), 500
            
        if not os.path.exists(extract_dir):
            print(f"Error: Extract directory not found at {extract_dir}")
            return jsonify({'error': f'Extract directory not found at {extract_dir}'}), 500
        
        # List the files to help debugging
        print(f"Files in extract dir: {os.listdir(extract_dir)}")
        if os.path.exists(config_dir):
            print(f"Files in config dir: {os.listdir(config_dir)}")
        
        # Handle config file modification and Go execution
        try:
            # Read the original config
            with open(config_path, 'r', encoding='utf-8') as file:
                original_content = file.read()
                
            # Find current stock code
            current_stock_match = re.search(r'StockCode\s*=\s*"([^"]*)"', original_content)
            current_stock = current_stock_match.group(1) if current_stock_match else "unknown"
            print(f"Current stock code: {current_stock}, replacing with: {param}")
                
            # Replace stock code in config file
            new_content = re.sub(r'StockCode\s*=\s*"[^"]*"', f'StockCode    = "{param}"', original_content)
            
            # Write modified config
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            # Verify the change was made
            with open(config_path, 'r', encoding='utf-8') as file:
                verification = file.read()
                verification_match = re.search(r'StockCode\s*=\s*"([^"]*)"', verification)
                if verification_match:
                    print(f"Verification - StockCode in config after update: {verification_match.group(1)}")
                else:
                    print("Warning: Could not verify stock code was updated")
                
            print(f"Config updated successfully, executing Go crawler...")
            



            go_path = r"D:\go1.23.8.windows-amd64\go\bin\go.exe"  # Đường dẫn đến go.exe
            extract_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'extract')

            result = subprocess.run(
                [go_path, 'run', 'main.go'],   # chỉ cần truyền main.go
                cwd=extract_dir,               # cwd là extract/ (chứa go.mod và main.go)
                capture_output=True,
                text=True,
                check=True
            )
            
            print("Go execution completed successfully")
            print(f"Go output: {result.stdout}")
            
            # Always restore original config
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(original_content)
                print("Original config restored")
                
            # Verify config was restored
            with open(config_path, 'r', encoding='utf-8') as file:
                restore_verification = file.read()
                restore_match = re.search(r'StockCode\s*=\s*"([^"]*)"', restore_verification)
                restored_stock = restore_match.group(1) if restore_match else "unknown"
                print(f"Config restored check - StockCode: {restored_stock}")
            
            # Return successful response
            return jsonify({
                'success': True, 
                'message': f'Crawling data for {param} completed successfully',
                'output': result.stdout
            }), 200
            
        except subprocess.CalledProcessError as e:
            print(f"Go execution error: {e}")
            print(f"Error output: {e.stderr}")
            
            # Restore config file
            if config_path and original_content:
                try:
                    with open(config_path, 'w', encoding='utf-8') as file:
                        file.write(original_content)
                        print("Original config restored after error")
                except Exception as restore_error:
                    print(f"Error restoring config: {restore_error}")
                    
            return jsonify({
                'error': 'Go program execution error', 
                'details': e.stderr
            }), 500
            
        except Exception as e:
            print(f"Error during config modification or Go execution: {str(e)}")
            
            # Restore config file
            if config_path and original_content:
                try:
                    with open(config_path, 'w', encoding='utf-8') as file:
                        file.write(original_content)
                        print("Original config restored after error")
                except Exception as restore_error:
                    print(f"Error restoring config: {restore_error}")
                    
            return jsonify({
                'error': 'Error during crawl process', 
                'details': str(e)
            }), 500
        
    except Exception as e:
        print(f"Unexpected error in admin_crawl: {str(e)}")
        
        # Attempt to restore config file if possible
        if config_path and original_content:
            try:
                with open(config_path, 'w', encoding='utf-8') as file:
                    file.write(original_content)
                    print("Original config restored after unexpected error")
            except Exception as restore_error:
                print(f"Error restoring config: {restore_error}")
                
        return jsonify({
            'error': 'Unexpected error', 
            'details': str(e)
        }), 500


# xử lý admin clean command
@app.route('/admin-clean', methods=['POST'])
def admin_clean():
    config_path = None
    original_content = None
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        print(f"Received clean command: {command}")

        # Kiểm tra cú pháp lệnh
        if not command.startswith('clean '):
            print("Error: Invalid command format")
            return jsonify({'error': 'Command must start with "clean"'}), 400

        # Parse the command để lấy mã cổ phiếu
        parts = command.split(' ', 1)
        if len(parts) < 2:
            print("Error: Missing parameter")
            return jsonify({'error': 'Missing stock code parameter'}), 400

        param = parts[1].strip()
        print(f"Processing clean for stock code: {param}")

        # Lấy đường dẫn tuyệt đối
        app_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(app_dir)
        transform_dir = os.path.join(project_dir, 'transform')
        config_path = os.path.join(transform_dir, 'config.txt')
        main_py_path = os.path.join(transform_dir, 'main.py')

        # Kiểm tra file tồn tại
        if not os.path.exists(config_path):
            print(f"Error: Config file not found at {config_path}")
            return jsonify({'error': f'Config file not found at {config_path}'}), 500
        if not os.path.exists(main_py_path):
            print(f"Error: Python script not found at {main_py_path}")
            return jsonify({'error': f'Python script not found at {main_py_path}'}), 500

        # Lưu lại nội dung gốc của config
        with open(config_path, 'r', encoding='utf-8') as file:
            original_content = file.read()

        try:
            # Thay thế mã cổ phiếu trong config
            new_content = re.sub(r'ma_cp\s*=\s*\w+', f'ma_cp = {param}', original_content)
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Config updated successfully, executing Python script...")

            # Chạy script Python với UTF-8
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            result = subprocess.run(
                ['python', main_py_path],
                cwd=transform_dir,
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
            print("Python script execution completed successfully")
            print(f"Python output: {result.stdout}")

            # Khôi phục lại config gốc
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(original_content)
            print("Original config restored")

            # Lưu thông tin file vào database
            # Lấy id mới nhất
            query_max_id = "SELECT MAX(id) as max_id FROM files"
            result_id = execute_query(query_max_id, ())
            new_id = (result_id[0]['max_id'] if result_id and result_id[0]['max_id'] is not None else 0) + 1

            folder_name = param
            location = r"D:\project_storage\ETL_Visualize_BCTC\load\csv"
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query_insert = "INSERT INTO files (id, folder_name, location, date) VALUES (%s, %s, %s, %s)"
            execute_query(query_insert, (new_id, folder_name, location, date_now))
            print(f"Inserted file info to DB: id={new_id}, folder_name={folder_name}, location={location}, date={date_now}")

            return jsonify({
                'success': True,
                'message': f'Clean data for {param} completed successfully',
                'output': result.stdout
            }), 200

        except subprocess.CalledProcessError as e:
            print(f"Python execution error: {e}")
            print(f"Error output: {e.stderr}")
            # Khôi phục lại config gốc
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(original_content)
            return jsonify({
                'error': 'Python script execution error',
                'details': e.stderr
            }), 500

        except Exception as e:
            print(f"Error during config modification or Python execution: {str(e)}")
            # Khôi phục lại config gốc
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(original_content)
            return jsonify({
                'error': 'Error during clean process',
                'details': str(e)
            }), 500

    except Exception as e:
        print(f"Clean Error: {str(e)}")
        # Khôi phục lại config gốc nếu có thể
        if config_path and original_content:
            try:
                with open(config_path, 'w', encoding='utf-8') as file:
                    file.write(original_content)
                print("Original config restored after unexpected error")
            except Exception as restore_error:
                print(f"Error restoring config: {restore_error}")
        return jsonify({'error': str(e)}), 500

# xử lý tải file csv về
import io
import zipfile
from flask import send_file

@app.route('/api/download-csv-folder', methods=['POST'])
def download_csv_folder():
    try:
        data = request.get_json()
        macp = data.get('macp', '').strip().upper()
        folder = r"D:\project_storage\ETL_Visualize_BCTC\load\csv"
        if not macp or len(macp) != 3:
            return jsonify({'error': 'Mã cp không hợp lệ'}), 400
        files = [f for f in os.listdir(folder) if f.lower().startswith(macp.lower()) and f.lower().endswith('.csv')]
        if not files:
            return jsonify({'error': 'Không có file nào để tải về'}), 404

        # Nén file vào zip
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fname in files:
                zf.write(os.path.join(folder, fname), arcname=fname)
        mem_zip.seek(0)
        return send_file(
            mem_zip,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{macp}_csv_files.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

                

# xử lý gọi báo cáo theo mã cổ phiếu
@app.route('/api/get-macp-list')
def get_macp_list():
    query = "SELECT macp, url, type FROM url"
    result = execute_query(query, ())
    return jsonify(result)


""" Khai báo chạy chương trình """
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
