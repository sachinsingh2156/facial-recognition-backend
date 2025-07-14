from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    unique_id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    image_width = serializers.IntegerField(required=False, min_value=1)
    image_height = serializers.IntegerField(required=False, min_value=1)
    image_depth = serializers.IntegerField(required=False, min_value=1)
    image_size_limit = serializers.IntegerField(required=False, min_value=1)  # in bytes or KB
    face_embedding = serializers.CharField(required=False)  # <-- Add required=False here

    class Meta:
        model = User
        fields = ['unique_id', 'name', 'face_embedding', 'image_width', 'image_height', 'image_depth', 'image_size_limit'] 