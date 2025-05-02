""" import các thư viện sử dụng """
from flask import Flask, render_template, session, request, jsonify
import os
from datetime import datetime, timedelta
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


@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')

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
    sql = data.get('sql')
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
        return jsonify({'error': str(e)}), 400



""" Khai báo chạy chương trình """
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
