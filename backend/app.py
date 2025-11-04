from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import boto3, bcrypt, uuid, datetime, os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET", "mysecretkey")

jwt = JWTManager(app)

# AWS setup
dynamodb = boto3.resource('dynamodb', region_name=os.getenv("AWS_REGION"))
s3 = boto3.client('s3')

users_table = dynamodb.Table(os.getenv("USERS_TABLE"))
files_table = dynamodb.Table(os.getenv("FILES_TABLE"))
bucket = os.getenv("S3_BUCKET")

# ---------- ROUTES FOR HTML PAGES ----------
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register')
def register_page():
    return render_template("register.html")

@app.route('/login')
def login_page():
    return render_template("login.html")

@app.route('/dashboard')
def dashboard_page():
    return render_template("dashboard.html")

# ---------- HEALTH CHECK ----------
@app.route('/api', methods=['GET'])
def api_root():
    return jsonify({"message": "✅ Smart Drive API is running successfully"}), 200


# ---------- REGISTER ----------
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    # Check if user exists
    existing = users_table.scan(
        FilterExpression="email = :e",
        ExpressionAttributeValues={":e": email}
    )
    if existing['Items']:
        return jsonify({'error': 'User already exists'}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_id = str(uuid.uuid4())

    users_table.put_item(Item={
        'user_id': user_id,
        'email': email,
        'password': hashed
    })

    return jsonify({'msg': 'User registered successfully'}), 201


# ---------- LOGIN ----------
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    res = users_table.scan(
        FilterExpression="email = :e",
        ExpressionAttributeValues={":e": email}
    )

    if not res['Items']:
        return jsonify({'error': 'User not found'}), 404

    user = res['Items'][0]
    if bcrypt.checkpw(password.encode(), user['password'].encode()):
        token = create_access_token(identity=user['user_id'])
        return jsonify({'token': token}), 200

    return jsonify({'error': 'Invalid password'}), 401


# ---------- UPLOAD FILE ----------
@app.route('/api/files/upload', methods=['POST'])
@jwt_required()
def upload():
    user_id = get_jwt_identity()

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    file_id = str(uuid.uuid4())
    key = f"{user_id}/{file.filename}"

    s3.upload_fileobj(file, bucket, key)
    file_url = f"https://{bucket}.s3.amazonaws.com/{key}"

    files_table.put_item(Item={
        'file_id': file_id,
        'owner_id': user_id,
        'filename': file.filename,
        'file_url': file_url,
        'upload_date': datetime.datetime.now().isoformat()
    })

    return jsonify({'file_url': file_url}), 201


# ---------- LIST FILES ----------
@app.route('/api/files', methods=['GET'])
@jwt_required()
def list_files():
    user_id = get_jwt_identity()
    res = files_table.scan(
        FilterExpression="owner_id = :u",
        ExpressionAttributeValues={":u": user_id}
    )
    return jsonify(res['Items']), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
