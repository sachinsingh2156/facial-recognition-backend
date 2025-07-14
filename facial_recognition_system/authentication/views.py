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
from django.db import IntegrityError

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
        try:
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
        except IntegrityError:
            return Response({"message": "A user with this username already exists. Please choose a different username."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AuthenticateUser(APIView):
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
            face_encoding = face_encodings[0]
            # Compare with all stored embeddings
            users = User.objects.all()
            for user in users:
                stored_encoding = np.array(eval(user.face_embedding))
                results = face_recognition.compare_faces([stored_encoding], face_encoding)
                if results[0]:
                    return Response({"message": "Authentication successful.", "name": user.name, "unique_id": user.unique_id}, status=status.HTTP_200_OK)
            return Response({"message": "Authentication failed. No matching user found."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
