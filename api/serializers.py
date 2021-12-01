from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class SendCodeSerializer(serializers.Serializer):
    """Serializer for sending code by e-mail"""
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Incorrect username')
        return value

    def validate(self, attrs):
        username_exists = User.objects.filter(
            username=attrs['username']).exists()
        email_exists = User.objects.filter(
            email=attrs['email']).exists()
        if username_exists and not email_exists:
            raise serializers.ValidationError('User already exists')
        if email_exists and not username_exists:
            raise serializers.ValidationError('User already exists')
        return attrs


class LogInSerializer(serializers.Serializer):
    """Serializer for logging in"""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for simple users"""
    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'bio',
                  'first_name',
                  'last_name',
                  'role'
                  )
        read_only_fields = ('role',)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews"""
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = UserSerializer(
            instance.author).data['username']
        return representation

    class Meta:
        model = Review
        fields = (
            'id', 'title', 'author', 'text', 'score', 'pub_date')
        read_only_fields = ('title', 'author', 'pub_date')

    def validate(self, attrs):
        review_obj_exists = Review.objects.filter(
            author=self.context.get('request').user,
            title=self.context.get('view').kwargs.get('title_id')
        ).exists()
        if review_obj_exists and self.context.get('request').method == 'POST':
            raise serializers.ValidationError('Вы уже оставляли отзыв')
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = UserSerializer(
            instance.author).data['username']
        return representation

    class Meta:
        model = Comment
        fields = (
            'id', 'review', 'author', 'text', 'pub_date'
        )
        read_only_fields = ('review', 'author', 'pub_date')


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for the genres"""
    slug = serializers.SlugField(
        max_length=50, required=True,
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )
    name = serializers.CharField(max_length=256, required=True)

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories"""
    slug = serializers.SlugField(
        max_length=50, required=True,
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )
    name = serializers.CharField(max_length=256, required=True)

    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    """Serializer for titles"""
    category_read = CategorySerializer(read_only=True, source='category')
    genre_read = GenreSerializer(many=True, read_only=True, source='genre')
    rating = serializers.IntegerField(read_only=True)
    description = serializers.CharField(required=False)
    category = serializers.SlugField(write_only=True, required=True)
    genre = serializers.ListField(
        child=serializers.SlugField(max_length=50),
        write_only=True, required=True
    )

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre_read',
            'category_read', 'category', 'genre')
        model = Title

    def create(self, validated_data):
        category_slug = validated_data.pop('category')
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)

        if category_slug is not None:
            category_obj = get_object_or_404(Category, slug=category_slug)
            title.category = category_obj
            title.save()

        if genres:
            for genre_slug in genres:
                genre_obj = Genre.objects.get(slug=genre_slug)
                title.genre.add(genre_obj)

        return title

    def update(self, instance, validated_data):
        if 'category' in validated_data:
            category_slug = validated_data.pop('category')
            if category_slug is not None:
                category_obj = get_object_or_404(Category, slug=category_slug)
                instance.category = category_obj
        if 'genres' in validated_data:
            genres = validated_data.pop('genre')
            if genres:
                instance.genre.clear()
                for genre_slug in genres:
                    genre_obj = Genre.objects.get(slug=genre_slug)
                    instance.genre.add(genre_obj)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def to_representation(self, value):
        rep = super().to_representation(value)
        rep['category'] = rep['category_read']
        del rep['category_read']
        rep['genre'] = rep['genre_read']
        del rep['genre_read']
        return rep
