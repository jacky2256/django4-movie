from typing import Any, Dict
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse

from django.views.generic import View, ListView, DetailView
from .models import Movie, Actor, Genre, Rating

from .forms import ReviewForm, RatingForm


class GenreYear:
    """Жанры и года выхода фильмов"""
    def get_genres(self):
        return Genre.objects.all()
    
    def get_year(self):
        return Movie.objects.filter(draft=False).values("year")
    

class MoviesListView(GenreYear, ListView):
    
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    paginate_by = 3
    # def get(self, request):
    #     movie_list = Movie.objects.all()
    #     context = {'movie_list' : movie_list}
    #     return render(request=request, template_name='movie/movie_list.html', context=context)



class MoviesDetailView(GenreYear, DetailView):
    
    model = Movie
    slug_field = 'url'

    # def get(self, request, slug):

    #     movie = Movie.objects.get(url=slug)
    #     context = {'movie' : movie}
    #     return render(request=request, template_name='movie/movie_detail.html', context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm()
        context["form"] = ReviewForm()
        return context
        

class AddReview(View):

    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = get_object_or_404(Movie, id=pk)
        if form.is_valid():
            review = form.save(commit=False)
            if request.POST.get('parent', None):
                review.parent_id = int(request.POST.get('parent'))
            review.movie = movie
            review.save()

        return redirect(movie.get_absolute_url())


class ActorView(GenreYear, DetailView):
    """Вывод информации о актерах"""
    model = Actor
    template_name = 'movie/actor.html'
    slug_field = "name"


class FilterMoviesView(GenreYear, ListView):
    """Фильтр фильмов"""

    paginate_by = 3

    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist("year")) |
            Q(genres__in=self.request.GET.getlist("genre"))
        ).distinct()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["year"] = ''.join([f"year={x}&" for x in self.request.GET.getlist("year")])
        context["genre"] = ''.join([f"genre={x}&" for x in self.request.GET.getlist("genre")])
        return context

class AddStarRating(View):
    """Добавление рейтинга фильму"""
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request, pk):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            movie = get_object_or_404(Movie, id=pk)
            return redirect(movie.get_absolute_url())
        else:
            return HttpResponse(status=400)
    
class Search(ListView):
    """Поиск фильмов"""
    paginate_by = 3

    def get_queryset(self):
        return Movie.objects.filter(title__icontains=self.request.GET.get("search"))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["search"] = f'search={self.request.GET.get("search")}&'
        return context