
 Cloud-Based Smart File Storage & Sharing System
A mini Google Drive–like web app built using AWS Cloud, Flask, DynamoDB, and S3.
 Project Overview

This project is a cloud-based file storage and sharing system where users can:

Register and log in securely

Upload files to the cloud

View or download uploaded files

Access public sharing links

It demonstrates how Flask, AWS S3, and DynamoDB can be integrated to build a scalable, secure, and serverless file-sharing solution.

Features

✅ User registration and login (JWT-based authentication)
✅ Secure file upload to AWS S3
✅ Cloud storage metadata in DynamoDB
✅ File sharing via pre-signed URLs
✅ Responsive front-end with Bootstrap
✅ Hosted on AWS EC2

 Tech Stack
Layer	Technology Used
Frontend	HTML, CSS, Bootstrap, JavaScript
Backend	Python Flask
Cloud Services	AWS S3 (storage), AWS DynamoDB (database), AWS EC2 (deployment)
Authentication	JSON Web Tokens (JWT)
Deployment	AWS EC2 Instance

⚙️ Architecture Overview
User → Flask App (EC2)
         ↓
      DynamoDB (User & File Metadata)
         ↓
        S3 Bucket (File Storage)

 Setup Instructions
1️⃣ Clone Repository
git clone https://github.com/<your-username>/smart-drive.git
cd smart-drive

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a .env file:

JWT_SECRET=your_jwt_secret
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
USERS_TABLE=UsersTable
FILES_TABLE=FilesTable

5️⃣ Run Flask App
python app.py


App runs on:
🔗 http://127.0.0.1:5000 (local)
🔗 http://(my public IP) :5000 (on EC2)

📂 Folder Structure
smart-drive/
│
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   └── dashboard.html
│
├── app.py
├── requirements.txt
├── .env
└── README.md


Learnings

Gained hands-on experience with Flask and AWS Cloud Services.

Understood how cloud storage works using Amazon S3.

Learned about IAM policies and DynamoDB for secure data management.

Deployed a full-stack web application on AWS EC2.

🏁 Project Status

✅ Backend and Frontend connected
✅ File upload, sharing, and download tested
✅ Hosted successfully on AWS EC2
🔜 Optional enhancements: File preview, role-based access, and UI improvements.

👨‍💻 Author

Jeevan Fenittus S
Cloud Computing Intern | AWS Enthusiast ☁️
📧 Email: jeevanfenittus@example.com
