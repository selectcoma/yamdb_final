from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Admin access for genres"""
    list_display = ('slug',)
    search_fields = ('slug',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Admin access for titles"""
    list_display = ('name', 'category', 'year')
    search_fields = ('name', 'category', 'year')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin access for categories"""
    list_display = ('slug', 'name')
    search_fields = ('slug', 'name')


class CommentInLine(admin.TabularInline):
    model = Comment


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin access for reviews"""
    list_display = ('title', 'author', 'text', 'pub_date')
    search_fields = ('title', 'author', 'text')
    inlines = [CommentInLine, ]
