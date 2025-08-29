from rest_framework import serializers
from django.contrib.auth.models import User


class UserInfoSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return obj.username


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['id', 'fullname', 'password', 'repeated_password', 'email']
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
            username=self.validated_data['fullname'],
            email=self.validated_data.get('email', ''),
        )
        account.set_password(pw)
        account.save()
        return account
