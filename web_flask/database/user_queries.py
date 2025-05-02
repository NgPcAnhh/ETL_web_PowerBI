from .db import DatabaseConnection
import mysql.connector
from mysql.connector import Error
import time

db = DatabaseConnection()

def execute_query(query, params):
    cursor = db.connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if cursor.with_rows:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount  # Return the number of affected rows for insert/update
        db.connection.commit()  # Commit the transaction
        return result
    except Error as e:
        print("Lỗi khi thực thi truy vấn:", e)
        return None
    finally:
        cursor.close()