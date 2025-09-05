"""
This module contains serializers for user authentication and registration.

Provides:
- UserInfoSerializer: Serializes user ID, email, and full name for display.
- RegistrationSerializer: Handles user registration with password confirmation
  and email uniqueness validation.

These serializers are used in the user registration and login API views to
validate input and format output data accordingly.
"""

# 1. Standard library
from django.contrib.auth.models import User

# 2. Third-party
from rest_framework import serializers



class UserInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying user ID, email, and full name.

    Full name is constructed by joining first and last names.

    Returned fields: 'id', 'email', 'fullname'.
    """
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        """Return concatenated first and last name."""
        return f"{obj.first_name} {obj.last_name}".strip()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.

    Validates uniqueness of email and matching passwords.
    Splits fullname into first_name and last_name for storage.

    Fields:
    - repeated_password (write-only): Confirm password entry.
    - fullname: User's full name.
    - email: Must be unique.
    - password: Write-only, securely stored.

    Returns the created User instance on save.
    """
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['id', 'fullname', 'password', 'repeated_password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        """Ensure email does not already exist in the system."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({"email": "Email is already in use."})
        return value

    def save(self):
        """Create and save user after validating password and splitting fullname."""
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        if pw != repeated_pw:
            raise serializers.ValidationError({"password": "Passwords doesn't match."})

        fullname = self.validated_data['fullname']
        parts = fullname.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        account = User(
            username=self.validated_data['email'],
            email=self.validated_data.get('email', ''),
            first_name = first_name,
            last_name = last_name
        )
        account.set_password(pw)
        account.save()
        return account
