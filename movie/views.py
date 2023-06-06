from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q


from django.views.generic import View, ListView, DetailView
from .models import Movie, Actor, Genre

from .forms import ReviewForm


class GenreYear:
    """Жанры и года выхода фильмов"""
    def get_genres(self):
        return Genre.objects.all()
    
    def get_year(self):
        return Movie.objects.filter(draft=False).values("year")
    

class MoviesListView(GenreYear, ListView):
    
    model = Movie
    queryset = Movie.objects.filter(draft=False)
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
    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist("year")) | 
            Q(genres__in=self.request.GET.getlist("genre"))
        )
        return queryset