# Facial Recognition API Backend

This backend provides facial recognition-based registration and authentication APIs, designed for integration with a frontend application (e.g., for auto-attendance or secure access systems).

---

## 🚀 Quick Start (with Docker)

### 1. **One-Command Setup**

Simply run this command to build and start everything in the background:
```bash
sudo docker-compose up -d --build
```

✅ **What this does automatically:**
- Builds the Docker image with all dependencies
- Applies database migrations automatically
- Starts the Django server on port **8053**
- Runs in background (terminal stays free for other work)
- API will be available at: [http://localhost:8053](http://localhost:8053)

### 2. **Verify It's Running**
```bash
sudo docker ps
```
You should see a container named `facial-recognition-backend_web_1` running.

### 3. **Test the API**
```bash
curl -X POST http://localhost:8053/api/authentication/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "testuser", "unique_id": "test123", "face_image": "base64_image_here"}'
```

### 4. **View Logs (Optional)**
```bash
sudo docker-compose logs -f
```
Press `Ctrl+C` to stop viewing logs (container keeps running).

### 5. **Stop the Server**
```bash
sudo docker-compose down
```

---

## 🐳 Docker Commands Reference

| Command | Description |
|---------|-------------|
| `sudo docker-compose up -d --build` | Build and run in background |
| `sudo docker ps` | Check running containers |
| `sudo docker-compose logs -f` | View live logs |
| `sudo docker-compose restart` | Restart services |
| `sudo docker-compose down` | Stop and remove containers |

---

## 🌐 Cross-Platform Support

This Docker setup works on:
- ✅ **Linux** (native Docker)
- ✅ **Windows** (Docker Desktop with WSL2)
- ✅ **macOS** (Docker Desktop)

**Windows users:** Install Docker Desktop and run the same commands in PowerShell or Command Prompt.

---

## 📡 API Endpoints

### 1. **Register User**
- **POST** `/api/authentication/register/`
- **Description:** Register a new user with a unique ID, name, and face image.
- **Request Body (JSON):**
  ```json
  {
    "unique_id": "user123",
    "name": "John Doe",
    "face_image": "<BASE64_IMAGE_STRING>",
    "image_width": 200,           // optional
    "image_height": 200,          // optional
    "image_depth": 3,             // optional
    "image_size_limit": 2048      // optional
  }
  ```
- **Response (Success):**
  ```json
  { "message": "User registered successfully." }
  ```

### 2. **Authenticate User**
- **POST** `/api/authentication/authenticate/`
- **Description:** Authenticate a user by face image only (unique_id is NOT required).
- **Request Body (JSON):**
  ```json
  {
    "face_image": "<BASE64_IMAGE_STRING>",
    "image_width": 200,           // optional
    "image_height": 200,          // optional
    "image_depth": 3,             // optional
    "image_size_limit": 2048      // optional
  }
  ```
- **Response (Success):**
  ```json
  { "message": "Authentication successful.", "name": "John Doe", "unique_id": "user123" }
  ```
- **Response (Failure):**
  ```json
  { "message": "Authentication failed. No matching user found." }
  ```
- **Note:**
  - The backend matches the provided face image against all registered users. The `unique_id` field in the request is ignored for authentication.

---

## 🏗️ Backend Architecture Diagram

<img width="2552" height="3840" alt="face-recognition" src="https://github.com/user-attachments/assets/f30b2984-e164-42b5-9735-8ddc1378567b" />


## 📸 How to Encode an Image to Base64

### **In Python:**
```python
import base64
with open('face.jpg', 'rb') as img_file:
    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
print(b64_string)
```

### **Online Tool:**
[https://base64.guru/converter/encode/image](https://base64.guru/converter/encode/image)

### **In JavaScript:**
```javascript
// For file upload
const fileToBase64 = (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.readAsDataURL(file);
  });
};
```

---

## 🔧 Configuration

### **Port Configuration**
- **Default Port:** 8053
- **Change Port:** Edit the `ENV PORT=8053` line in `Dockerfile` before building
- **Or use environment variable:**
  ```bash
  sudo docker run -e PORT=9000 -p 9000:9000 facial-recognition
  ```

### **Database**
- Uses SQLite by default (good for development)
- Database migrations run automatically on container startup
- No manual migration commands needed!

---

## 🧪 Testing

### **Automated Test Script**
```bash
python3 test_facial_recognition_api.py
```

### **Manual Testing with curl**
```bash
# Registration
curl -X POST http://localhost:8053/api/authentication/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "unique_id": "john123", "face_image": "YOUR_BASE64_IMAGE"}'

# Authentication
curl -X POST http://localhost:8053/api/authentication/authenticate/ \
  -H "Content-Type: application/json" \
  -d '{"face_image": "YOUR_BASE64_IMAGE"}'
```

---

## 🔍 Troubleshooting

### **Common Issues:**

| Issue | Solution |
|-------|----------|
| Port 8053 already in use | Change port in Dockerfile or stop other services |
| Container won't start | Check logs: `sudo docker-compose logs` |
| API returns 404 | Ensure you're using the correct endpoints |
| Face recognition fails | Ensure image is clear and contains a face |
| Build takes long time | This is normal for first build (downloading dependencies) |

### **Reset Everything:**
```bash
sudo docker-compose down
sudo docker system prune -f
sudo docker-compose up -d --build
```

---

## 🚀 Production Deployment

### **For Production:**
1. Change `DEBUG = False` in Django settings
2. Use PostgreSQL instead of SQLite
3. Set up proper environment variables
4. Use HTTPS/SSL certificates
5. Set up proper logging and monitoring

### **Environment Variables:**
```bash
# docker-compose.yml
environment:
  - DEBUG=False
  - DATABASE_URL=postgresql://user:pass@host:port/db
  - SECRET_KEY=your-secret-key
```

---

## 📚 Integration Tips

- All requests and responses are in JSON
- The backend expects a base64-encoded image string for `face_image`
- Optional image parameters can be sent for custom processing
- On registration, the backend extracts and stores a face encoding
- On authentication, it compares the new encoding to stored ones
- Error messages are returned in JSON for easy frontend handling

---

## 🆘 Need Help?

- **Check logs:** `sudo docker-compose logs -f`
- **Test endpoints:** Use Postman or curl
- **Database issues:** Container automatically handles migrations
- **Performance:** Ensure good lighting and clear face images

---

## 👨‍💻 Developed By

**Sachin Singh**  
M.Tech CSE, IIT Jodhpur

[LinkedIn](https://www.linkedin.com/in/sachinsingh2156) • [GitHub](https://github.com/sachinsingh2156)

---

## ⭐ Features

- 🔐 **Secure facial recognition** using advanced ML models
- 🐳 **Docker containerized** for easy deployment
- 🌐 **Cross-platform** support (Windows, macOS, Linux)
- 🚀 **One-command setup** with automatic migrations
- 📱 **RESTful API** for easy frontend integration
- 🔄 **Background running** keeps terminal free
- 📊 **Built-in logging** and error handling
- 🧪 **Test scripts included** for validation
