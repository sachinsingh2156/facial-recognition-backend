import base64
import numpy as np
import cv2
import face_recognition
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer

# Helper function to decode base64 image to numpy array
def decode_base64_image(base64_string):
    try:
        img_data = base64.b64decode(base64_string)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None

class RegisterUser(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            face_image_b64 = request.data.get('face_image')
            if not face_image_b64:
                return Response({"message": "face_image is required."}, status=status.HTTP_400_BAD_REQUEST)
            img = decode_base64_image(face_image_b64)
            if img is None:
                return Response({"message": "Invalid image data."}, status=status.HTTP_400_BAD_REQUEST)
            face_locations = face_recognition.face_locations(img)
            if not face_locations:
                return Response({"message": "No face found in the image."}, status=status.HTTP_400_BAD_REQUEST)
            face_encodings = face_recognition.face_encodings(img, face_locations)
            if not face_encodings:
                return Response({"message": "Could not extract face encoding."}, status=status.HTTP_400_BAD_REQUEST)
            face_encoding = face_encodings[0].tolist()  # Convert numpy array to list for storage
            serializer.save(face_embedding=face_encoding)
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthenticateUser(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            image_width = serializer.validated_data.get('image_width')
            image_height = serializer.validated_data.get('image_height')
            image_depth = serializer.validated_data.get('image_depth')
            image_size_limit = serializer.validated_data.get('image_size_limit')
            # Use these parameters in your image processing logic as needed
            # ...
        unique_id = request.data.get('unique_id')
        face_image_b64 = request.data.get('face_image')
        if not unique_id or not face_image_b64:
            return Response({"message": "unique_id and face_image are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(unique_id=unique_id)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        img = decode_base64_image(face_image_b64)
        if img is None:
            return Response({"message": "Invalid image data."}, status=status.HTTP_400_BAD_REQUEST)
        face_locations = face_recognition.face_locations(img)
        if not face_locations:
            return Response({"message": "No face found in the image."}, status=status.HTTP_400_BAD_REQUEST)
        face_encodings = face_recognition.face_encodings(img, face_locations)
        if not face_encodings:
            return Response({"message": "Could not extract face encoding."}, status=status.HTTP_400_BAD_REQUEST)
        face_encoding = face_encodings[0]
        # Compare with stored embedding
        stored_encoding = np.array(eval(user.face_embedding))
        results = face_recognition.compare_faces([stored_encoding], face_encoding)
        if results[0]:
            return Response({"message": "Authentication successful."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Authentication failed."}, status=status.HTTP_401_UNAUTHORIZED)
