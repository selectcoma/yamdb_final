import datetime as dt

from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Avg, UniqueConstraint
from django.core.exceptions import ValidationError

User = get_user_model()


class Category(models.Model):
    """Model for categories"""
    name = models.CharField(
        verbose_name='Category name',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
    )

    class Meta:
        verbose_name = 'Category',
        verbose_name_plural = 'Categories',
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Model for  genres"""
    name = models.CharField(
        verbose_name='Genre name',
        max_length=256,
        blank=True,
        default='no genre'
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
    )

    class Meta:
        verbose_name = 'Genre',
        verbose_name_plural = 'Genres',
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Model for titles"""
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Category'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,
        verbose_name='Genree'
    )

    name = models.CharField(
        verbose_name='Name',
        max_length=256)
    year = models.PositiveIntegerField()

    @property
    def rating(self):
        score = self.reviews.filter(
            title=self
        ).aggregate(Avg('score'))
        return score['score__avg']

    description = models.TextField(
        verbose_name='Description',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Title',
        verbose_name_plural = 'Titles',
        ordering = ('-year',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.year > dt.datetime.today().year:
            raise ValidationError('Wrong year')
        super().save(*args, **kwargs)


class Review(models.Model):
    """Model for reviews"""
    SCORE_CHOICES = [
        (i, i) for i in range(1, 11)
    ]
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Title'

    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Author',
    )
    text = models.TextField(
        verbose_name='Text',
        validators=[MaxLengthValidator(90000, message='Too many characters')]
    )
    score = models.PositiveIntegerField(
        choices=SCORE_CHOICES,
        verbose_name='Score',

    )
    pub_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Review',
        verbose_name_plural = 'Reviews',
        ordering = ('-pub_date',)
        constraints = [
            UniqueConstraint(
                fields=('author', 'title'),
                name='unique_author_review'
            )
        ]

    def __str__(self):
        return self.text[:50]


class Comment(models.Model):
    """Model for comments"""
    review = models.ForeignKey(
        Review,
        verbose_name='Review',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Author',
        related_name='comments',
        on_delete=models.CASCADE,

    )
    text = models.TextField(
        'Comment text',
        validators=[MaxLengthValidator(
            2000,
            message='Превышен лимит знаков')]
    )
    pub_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comment',
        verbose_name_plural = 'Comments'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:50]
