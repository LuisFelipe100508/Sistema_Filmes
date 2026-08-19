from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("filmes/", views.lista_filmes, name="lista_filmes"),
    path("filmes-atores/", views.lista_filme_atores, name="lista_filme_atores"),
    path("series/", views.lista_series, name="lista_series"),
    path("episodios/", views.lista_episodios, name="lista_episodios"),
    path("temporadas/", views.lista_temporadas, name="lista_temporadas"),
    path("generos/", views.lista_generos, name="lista_generos"),
    path("pessoas/", views.lista_pessoas, name="lista_pessoas"),
    path("paises/", views.lista_paises, name="lista_paises"),
    path("continentes/", views.lista_continentes, name="lista_continentes"),
]