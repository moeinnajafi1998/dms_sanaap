from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# Serializer for User model
class UserSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'groups', 'is_staff', 'is_active']
        
    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        user = User.objects.create(**validated_data)
        user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.groups.set(groups)
        return instance
