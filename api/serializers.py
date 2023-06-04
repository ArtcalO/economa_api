from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import *
from django.db import transaction
from django.contrib.auth.models import Group
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.exceptions import MultipleObjectsReturned
from rest_framework.exceptions import APIException

class TokenPairSerializer(TokenObtainPairSerializer):


	def validate(self, attrs):
		data = super(TokenPairSerializer, self).validate(attrs)
		data['id'] = self.user.id
		data['is_admin'] = self.user.is_superuser
		data['username'] = self.user.username
		data['first_name'] = self.user.first_name
		data['last_name'] = self.user.last_name

		if self.user.is_superuser:
			data['Personnels'] = Personnel.objects.all().count()
			data['eleves'] = Eleve.objects.all().count()
			
		return data


class GroupSerializer(serializers.ModelSerializer):

	class Meta:
		model = Group
		fields = "__all__"

class PasswordResetSerializer(serializers.Serializer):
	reset_code = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
	@transaction.atomic()
	def update(self, instance, validated_data):
		user = instance
		username = validated_data.get('username')
		first_name = validated_data.get('first_name')
		last_name = validated_data.get('last_name')
		nouv_password = validated_data.get('nouv_password')
		anc_password = validated_data.get('anc_password')
		if check_password(anc_password, self.context['request'].user.password):
			if username:
				user.username = username
			if first_name:
				user.first_name = first_name
			if last_name:
				user.last_name = last_name
			if password:
				user.set_password(password)
			user.save()
			return user
		return user

	class Meta:
		model = User
		read_only_fields = "is_active", "is_staff","password"
		exclude = "last_login", "is_staff", "date_joined"
		extra_kwargs = {
			'username': {
				'validators': [UnicodeUsernameValidator()]
			}
		}

class PersonnelSerializer(serializers.ModelSerializer):
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		user = User.objects.get(id=instance.user.id)
		group = [group.name for group in user.groups.all()]
		representation['user'] = {
			'id': user.id,
			'username': user.username,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'email': user.email,
			'groups': group
		}
		return representation
	user = UserSerializer()
	class Meta:
		model = Personnel
		fields = '__all__'

	@transaction.atomic()
	def update(self, instance, validated_data):
		instance.telephone = validated_data.get('telephone', instance.telephone)
		instance.genre = validated_data.get('genre', instance.genre)

		user_prof_data = validated_data.get('user')
		user_prof = instance.user
		user_prof.username = user_prof_data["username"]
		user_prof.first_name = user_prof_data["first_name"]
		user_prof.last_name = user_prof_data["last_name"]
		user_prof.save()
		instance.user=user_prof
		instance.save()
		return instance
		
class EleveSerializer(serializers.ModelSerializer):
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		if(instance.user):
			user = User.objects.get(id=instance.user.id)
			group = [group.name for group in user.groups.all()]
			representation['user'] = {
				'id': user.id,
				'username': user.username,
				'first_name': user.first_name,
				'last_name': user.last_name,
				'groups': group
			}
		if(instance.classe):
			representation["classe"]=ClasseSerializer(instance.classe, many=False).data
		return representation
	user = UserSerializer()
	class Meta:
		model = Eleve
		read_only_fields = 'pin',
		fields = '__all__'
		
class NiveauSerializer(serializers.ModelSerializer):
	class Meta:
		model = Niveau
		fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		niveau = NiveauSerializer(instance.niveau, many=False).data
		representation['niveau'] = {
			'id': niveau.get('id'),
			'nom': niveau.get('nom'),
		}
		return representation
	class Meta:
		model = Section
		fields = '__all__'

class ClasseSerializer(serializers.ModelSerializer):
	def to_representation(self, instance):
		representation = super(ClasseSerializer,self).to_representation(instance)
		niveau = NiveauSerializer(instance.niveau, many=False).data
		representation['niveau'] = {
			'id': niveau.get('id'),
			'nom': niveau.get('nom'),
		}
		section = SectionSerializer(instance.section, many=False).data
		representation['section'] = {
			'id': section.get('id'),
			'nom': section.get('nom'),
		}
		representation['classe_full_name'] = f"{instance.nom} {niveau.get('nom')} {section.get('nom')}"
		return representation
	class Meta:
		model = Classe
		fields = '__all__'
