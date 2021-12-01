import uuid

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from reviews.models import Category, Genre, Review, Title
from users.models import User
from .mixins import CustomMixin

from .filters import TitleFilter
from .permissions import (AuthorOrReadOnlyPermission, IsAdmin,
                          IsAdminOrReadOnly, IsAuthenticatedOrReadOnly)
from .serializers import (AdminUserSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer, LogInSerializer,
                          ReviewSerializer, SendCodeSerializer,
                          TitleSerializer, UserSerializer)


@api_view(['POST'])
def send_code(request):
    """View for sending code to a registered user"""
    serializer = SendCodeSerializer(data=request.data)
    email = request.data.get('email')
    username = request.data.get('username')
    confirmation_code = str(uuid.uuid4())
    if serializer.is_valid():

        if User.objects.filter(email=email, username=username).exists():
            user = User.objects.get(email=email, username=username)
            user.confirmation_code = confirmation_code
        else:
            User.objects.create_user(email=email, username=username)
        mail_subject = 'API_Yamdb: Your authentication code'
        mail_message = f'Скопируйте код: {confirmation_code}'
        send_mail(mail_subject, mail_message, 'API_Yamdb <admin@yamdb.ru>',
                  (email,), fail_silently=True)
        return Response(
            request.data,
            status=status.HTTP_200_OK)
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_token(request):
    """View for getting the authentication token"""
    serializer = LogInSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.data.get('username')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if confirmation_code == str(user.confirmation_code):
            token = RefreshToken.for_user(user)
            return Response({f'Your token: {token.access_token}'},
                            status=status.HTTP_200_OK)
        return Response('Wrong code',
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminViewSet(viewsets.ModelViewSet):
    """View-set for admins"""
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    filter_fields = ('role',)
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']


class UserInfo(APIView):
    """View for getting user info"""
    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, username=request.user.username)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response('You are not authenticated',
                        status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, username=request.user.username)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response('You are not authenticated',
                        status=status.HTTP_401_UNAUTHORIZED)


class ReviewViewSet(viewsets.ModelViewSet):
    """View for the reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        AuthorOrReadOnlyPermission
    ]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        author = self.request.user
        serializer.save(
            author=author,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    """View for comments"""
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        AuthorOrReadOnlyPermission
    ]

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(
            author=self.request.user,
            review=review
        )


class GenreViewSet(CustomMixin):
    """View for genres"""
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    queryset = Genre.objects.all()
    lookup_field = 'slug'


class CategoryViewSet(CustomMixin):
    """View for categories"""
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    queryset = Category.objects.all()
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """View for titles"""
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = TitleFilter
    filterset_fields = ('name', 'year')
    queryset = Title.objects.all()
