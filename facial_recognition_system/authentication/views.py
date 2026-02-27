import base64
import numpy as np
import cv2
import face_recognition
from PIL import Image
import imagehash
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from django.db import IntegrityError

# Face match threshold: same person if distance <= this. Tune (e.g. 0.35–0.45) if needed.
FACE_MATCH_TOLERANCE = 0.4

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
                
                # Generate image hash for duplicate detection (fast O(1) lookup)
                try:
                    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    image_hash = str(imagehash.phash(img_pil))
                except Exception as e:
                    return Response({"message": f"Error generating image hash: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Check if exact same image already exists (fast database lookup)
                existing_user = User.objects.filter(image_hash=image_hash).first()
                if existing_user:
                    return Response({
                        "message": f"This exact image is already registered for user ID: {existing_user.unique_id} (Name: {existing_user.name}). Please use a different photograph."
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                face_locations = face_recognition.face_locations(img)
                if not face_locations:
                    return Response({"message": "No face found in the image."}, status=status.HTTP_400_BAD_REQUEST)
                face_encodings = face_recognition.face_encodings(img, face_locations)
                if not face_encodings:
                    return Response({"message": "Could not extract face encoding."}, status=status.HTTP_400_BAD_REQUEST)
                face_encoding = face_encodings[0].tolist()  # Convert numpy array to list for storage
                face_encoding_np = np.array(face_encoding)

                # Reject if this face is already registered under another member ID
                for user in User.objects.exclude(face_embedding=""):
                    try:
                        stored_encoding = np.array(eval(user.face_embedding))
                        distance = face_recognition.face_distance([stored_encoding], face_encoding_np)[0]
                        if distance <= FACE_MATCH_TOLERANCE:
                            return Response({
                                "message": f"This face is already registered with another member (unique_id: {user.unique_id}, name: {user.name}). One person cannot be registered under multiple member IDs."
                            }, status=status.HTTP_400_BAD_REQUEST)
                    except (ValueError, SyntaxError):
                        continue

                # Save with image hash
                serializer.save(face_embedding=face_encoding, image_hash=image_hash)
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
            
            # Find the best match instead of returning the first match
            users = User.objects.exclude(face_embedding="")
            best_match = None
            best_distance = float('inf')

            for user in users:
                stored_encoding = np.array(eval(user.face_embedding))
                face_distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
                if face_distance <= FACE_MATCH_TOLERANCE and face_distance < best_distance:
                    best_match = user
                    best_distance = face_distance
            
            if best_match:
                return Response({
                    "message": "Authentication successful.", 
                    "name": best_match.name, 
                    "unique_id": best_match.unique_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Authentication failed. No matching user found."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUser(APIView):
    def delete(self, request, unique_id, *args, **kwargs):
        try:
            user = User.objects.get(unique_id=unique_id)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
