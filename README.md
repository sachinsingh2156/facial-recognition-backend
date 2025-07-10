# Facial Recognition API Backend

This backend provides facial recognition-based registration and authentication APIs, designed for integration with a frontend application (e.g., for auto-attendance or secure access systems).

---

## Quick Start (with Docker)

### 1. **Build and Run the Backend**

Open a terminal in the project root directory and run:
```bash
docker-compose up --build
```
- This command builds the Docker image (if not already built) and starts the Django server inside a container.
- The API will be available at: [http://localhost:8000](http://localhost:8000)

### 2. **Apply Migrations (First Run Only)**
After the container is running for the first time, you need to apply database migrations:
```bash
docker ps  # Find the running container name (e.g., facial_recognition_app-web-1)
docker exec -it <container_name> python facial_recognition_system/manage.py migrate
```
Replace `<container_name>` with the actual name from the previous command.

### 3. **Stopping the Server**
- Press `Ctrl+C` in the terminal running `docker-compose up` to stop the server.
- To stop and remove containers, run:
  ```bash
  docker-compose down
  ```


  

### 4. **Rebuilding the Image (After Code Changes)**
If you change dependencies or system packages, rebuild the image:
```bash
docker-compose build
```

### 5. **Viewing Logs**
To view logs from the running container:
```bash
docker-compose logs
```

### 6. **Accessing the Django Admin**
- Visit [http://localhost:8000/admin/](http://localhost:8000/admin/) in your browser.
- You may need to create a superuser:
  ```bash
  docker exec -it <container_name> python facial_recognition_system/manage.py createsuperuser
  ```

### 7. **Common Issues & Troubleshooting**
- **Port already in use:** Make sure nothing else is running on port 8000.
- **Module not found:** Ensure you have run `docker-compose build` after changing dependencies.
- **Database errors:** Make sure migrations are applied as shown above.
- **File changes not reflected:** If you change code, restart the container or use `docker-compose up --build`.

---

## API Endpoints

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
- **Description:** Authenticate a user by unique ID and face image.
- **Request Body (JSON):**
  ```json
  {
    "unique_id": "user123",
    "face_image": "<BASE64_IMAGE_STRING>",
    "image_width": 200,           // optional
    "image_height": 200,          // optional
    "image_depth": 3,             // optional
    "image_size_limit": 2048      // optional
  }
  ```
- **Response (Success):**
  ```json
  { "message": "Authentication successful." }
  ```
- **Response (Failure):**
  ```json
  { "message": "Authentication failed." }
  ```

---

## Backend Architecture Diagram

<img width="2613" height="3840" alt="architecture" src="https://github.com/user-attachments/assets/51f2fd4d-563a-4a10-ac90-1e478414bfe6" />

## How to Encode an Image to Base64

In Python:
```python
import base64
with open('face.jpg', 'rb') as img_file:
    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
print(b64_string)
```
- Use the output as the value for `face_image` in your API requests.

Or use an online tool: [https://base64.guru/converter/encode/image](https://base64.guru/converter/encode/image)

---

## Integration Tips
- All requests and responses are in JSON.
- The backend expects a base64-encoded image string for `face_image`.
- Optional image parameters (`image_width`, `image_height`, `image_depth`, `image_size_limit`) can be sent for custom processing (if needed by the backend).
- On registration, the backend extracts and stores a face encoding. On authentication, it compares the new encoding to the stored one.
- Error messages are returned in JSON for easy handling in the frontend.

---


## Example Test Script

See `test_facial_recognition_api.py` for a sample Python script to test registration and authentication.

---

## Need Help?
- If you have questions about request formats or integration, contact the backend developer.
- For troubleshooting, check Docker logs or use Postman/curl to test endpoints directly.

## Developed By

**Sachin Singh**
M.Tech CSE, IIT Jodhpur

[LinkedIn](https://www.linkedin.com/in/sachinsingh2156) • [GitHub](https://github.com/sachinsingh2156)
