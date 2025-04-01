import sqlite3

# Kết nối đến database (tự động tạo file users.db nếu chưa có)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Tạo bảng lưu thông tin người dùng
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()
