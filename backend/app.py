from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import boto3, bcrypt, uuid, datetime, os
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Attr

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET")

jwt = JWTManager(app)

# Initialize AWS resources
dynamodb = boto3.resource('dynamodb', region_name=os.getenv("AWS_REGION"))
s3 = boto3.client('s3')

# DynamoDB tables and S3 bucket
users_table = dynamodb.Table(os.getenv("USERS_TABLE"))
files_table = dynamodb.Table(os.getenv("FILES_TABLE"))
bucket = os.getenv("S3_BUCKET")

# ---------- ROOT ROUTE ----------
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "✅ Smart Drive API is running successfully"}), 200


# ---------- USER REGISTRATION ----------
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email']
    password = data['password']

    # Check if user already exists
    res = users_table.scan(
        FilterExpression=Attr('email').eq(email)
    )
    if res['Items']:
        return jsonify({'error': 'User already exists'}), 409

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_id = str(uuid.uuid4())

    users_table.put_item(Item={
        'user_id': user_id,
        'email': email,
        'password': hashed_pw
    })

    return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201


# ---------- USER LOGIN ----------
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email']
    password = data['password']

    res = users_table.scan(
        FilterExpression=Attr('email').eq(email)
    )

    if not res['Items']:
        return jsonify({'error': 'User not found'}), 404

    user = res['Items'][0]

    if bcrypt.checkpw(password.encode(), user['password'].encode()):
        token = create_access_token(identity=user['user_id'])
        return jsonify({'token': token}), 200

    return jsonify({'error': 'Invalid password'}), 401


# ---------- FILE UPLOAD ----------
@app.route('/api/files/upload', methods=['POST'])
@jwt_required()
def upload_file():
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
        FilterExpression=Attr('owner_id').eq(user_id)
    )
    return jsonify(res['Items']), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
