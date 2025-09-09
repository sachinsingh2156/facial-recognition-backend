import base64
import requests

# Helper function to convert image to base64 string
def image_to_base64(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Set your image path here
image_path = 'face_test.jpeg'  # Replace with your image file

# Convert image to base64
base64_image = image_to_base64(image_path)

# Registration endpoint
register_url = 'http://localhost:8053/api/authentication/register/'
register_payload = {
    "unique_id": "ss2233",
    "name": "sahil",
    "face_image": base64_image
}
register_response = requests.post(register_url, json=register_payload)
print("Registration Response:", register_response.status_code, register_response.json())

# Authentication endpoint
auth_url = 'http://localhost:8053/api/authentication/authenticate/'
auth_payload = {
    "face_image": base64_image
}
auth_response = requests.post(auth_url, json=auth_payload)
print("Authentication Response:", auth_response.status_code, auth_response.json())