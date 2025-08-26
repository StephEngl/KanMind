from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'location', 'birth_date']

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'repeated_password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError({"email": "Email is already in use."})
            return value

    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        if pw != repeated_pw:
            raise serializers.ValidationError({"password": "Passwords doesn't match."})
        
        account = User(
            username=self.validated_data['username'],
            email=self.validated_data.get('email', ''),
            first_name=self.validated_data.get('first_name', ''),
            last_name=self.validated_data.get('last_name', '')
        )
        account.set_password(pw)
        account.save()
        return account
