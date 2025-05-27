# 🖼️ Image Hosting Service

A lightweight image upload and hosting web app written in Python with a minimal frontend. Supports direct links, preview gallery, and full Docker containerization.

---

## 🚀 Features

- Upload `.jpg`, `.png`, `.gif` files (up to 5MB)
- View uploaded images in a browser preview
- Copy direct link to any image
- Files served through **Nginx**
- Backend built in pure **Python 3.12+** (`http.server`)
- Dockerized using **Docker Compose**

---

## 🧰 Technologies Used

- Python (standard library + Pillow)
- Nginx
- Docker & Docker Compose
- HTML + JS (no frameworks)

---

## 📂 Project Structure
ProjectImageService/
├── app.py  
├── static/
├── images/
├── logs/
├── requirements.txt 
├── docker-compose.yml 
├── Dockerfile 
├── nginx.conf
└── README.md 

---

## ⚙️ How to Run

### 1. Prerequisites:
- Docker
- Docker Compose

### 2. Run the app:
docker compose up --build

### 3. Access:
- Upload page: http://localhost:8000
- Uploaded image links: http://localhost:8000/images/filename.jpg
 
 ---

🛡️ Functional & Non-Functional Requirements
	•	File validation on size and type
	•	Real-time feedback on upload status
	•	Auto-generated unique filenames
	•	Gallery view available at /gallery
	•	Images and logs persist via Docker volumes
	•	Easy to extend and modify
