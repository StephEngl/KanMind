from app_board.models import Board
from rest_framework import serializers

class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = ["id", "title", "member_count"]

    def get_member_count(self, obj):
        return obj.members.count()