from django.urls import path
from . import views

app_name = 'authors'

urlpatterns = [
    path('', views.AuthorListView.as_view(), name='author_list'),
    path('<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('add/', views.AuthorCreateView.as_view(), name='author_create'),
    path('<int:pk>/edit/', views.AuthorUpdateView.as_view(), name='author_update'),
    path('<int:pk>/delete/', views.AuthorDeleteView.as_view(), name='author_delete'),
]
