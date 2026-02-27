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
unique_id = 'ss2233'
register_payload = {
    "unique_id": unique_id,
    "name": "sahil",
    "face_image": base64_image
}
register_response = requests.post(register_url, json=register_payload)
print("Registration Response:", register_response.status_code)
try:
    print("Registration JSON:", register_response.json())
except requests.exceptions.JSONDecodeError:
    print("Registration Response Text:", register_response.text)

# Authentication endpoint
auth_url = 'http://localhost:8053/api/authentication/authenticate/'
auth_payload = {
    "face_image": base64_image
}
auth_response = requests.post(auth_url, json=auth_payload)
print("Authentication Response:", auth_response.status_code)
try:
    print("Authentication JSON:", auth_response.json())
except requests.exceptions.JSONDecodeError:
    print("Authentication Response Text:", auth_response.text)

# Delete endpoint
delete_url = f'http://localhost:8053/api/authentication/delete/{unique_id}/'
delete_response = requests.delete(delete_url)
print("Delete Response:", delete_response.status_code)
try:
    print("Delete JSON:", delete_response.json())
except requests.exceptions.JSONDecodeError:
    print("Delete Response Text:", delete_response.text)