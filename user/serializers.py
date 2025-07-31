from django.contrib.auth import get_user_model
from rest_framework import serializers
from wines.serializers import WineListSerializer

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "email", "password")
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("is_staff",)


class UserDetailSerializer(BaseUserSerializer):

    saved_wines = WineListSerializer(many=True, read_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "saved_wines",
        )
