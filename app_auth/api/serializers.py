from rest_framework import serializers
from django.contrib.auth.models import User


class UserInfoSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


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

        print("FULLNAME:", self.validated_data.get('fullname'))
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
