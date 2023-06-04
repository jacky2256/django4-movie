from django import template
from movie.models import Category, Movie


register = template.Library()


@register.simple_tag()
def get_categories():
    """Вывод всех категорий"""
    return Category.objects.all()


@register.inclusion_tag("movie/tags/last_movie.html")
def show_last_movies(count=5):
    movies = Movie.objects.order_by("id")[:count]
    return {"last_movies": movies}