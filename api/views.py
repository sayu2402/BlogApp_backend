from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Sum

# Restframework
from rest_framework import status
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import SessionAuthentication


from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

# Others
import json
import random

# Custom Imports
from api import serializer as api_serializer
from api import models as api_models


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = api_models.User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer
    authentication_classes = [SessionAuthentication]


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.ProfileSerializer
    authentication_classes = [SessionAuthentication]

    def get_object(self):
        user_id = self.kwargs["user_id"]
        user = api_models.User.objects.get(id=user_id)
        profile = api_models.Profile.objects.get(user=user)
        return profile


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        return api_models.Category.objects.all()


class PostCategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        category_slug = self.kwargs["category_slug"]
        category = api_models.Category.objects.get(slug=category_slug)
        posts = api_models.Post.objects.get(category=category, status="Active")
        return posts


class PostListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        return api_models.Post.objects.filter(status="Activate")


class PostDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def get_object(self):
        slug = self.kwargs["slug"]
        post = api_models.Post.objects.get(slug=slug, status="Activate")
        post.views += 1
        post.save()
        return post


class LikePostAPIView(APIView):
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        user_id = request.data["user_id"]
        post_id = request.data["post_id"]

        user = api_models.User.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id)

        if user in post.likes.all():
            post.likes.remove(user)
            return Response({"message": "Post Disliked"}, status=status.HTTP_200_OK)
        else:
            post.likes.add(user)

            api_models.Notification.objects.create(
                user=post.user, post=post, type="Like"
            )
            return Response({"message": "Post Liked"}, status=status.HTTP_201_CREATED)
