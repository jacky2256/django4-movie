from django.urls import path
from . import views

urlpatterns = [
    path('', views.MoviesListView.as_view()),
    path('<slug:slug>/', views.MoviesDetailView.as_view(), name='movie_detail'),
    path('review/<int:pk>/', views.AddReview.as_view(), name='add_review')
]