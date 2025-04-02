from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import jwt
import datetime

# Cấu hình Flask
app = Flask(__name__)

# Lấy DATABASE_URL từ biến môi trường và kiểm tra định dạng
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("❌ ERROR: DATABASE_URL is not set. Please check environment variables!")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Kết nối database
db = SQLAlchemy(app)

# Khóa bí mật JWT
SECRET_KEY = "your_secret_key"  # 🔴 Cần đặt giá trị mạnh hơn hoặc lấy từ biến môi trường

# Tạo bảng User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# API kiểm tra server có hoạt động không
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

# API đăng ký tài khoản
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Kiểm tra username và password có hợp lệ không
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return jsonify({"message": "Username can only contain letters, numbers, and underscores"}), 400
    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    # Kiểm tra username đã tồn tại chưa
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Username already exists"}), 400

    # Lưu mật khẩu dưới dạng hash
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# API đăng nhập + JWT Token
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Kiểm tra user có tồn tại không
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid username or password"}), 401

    # Tạo JWT Token
    token = jwt.encode(
        {"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({"message": "Login successful", "token": token}), 200

# Kiểm tra kết nối database trước khi chạy server
try:
    with app.app_context():
        db.create_all()
        db.engine.connect()
        print("✅ Database connected successfully!")
except Exception as e:
    print(f"❌ ERROR: Cannot connect to database: {str(e)}")
    exit(1)  # Dừng chương trình nếu không kết nối được database

# Chạy server Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

