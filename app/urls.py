from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("filme/<int:filme_id>/", views.detalhe_filme, name="detalhe_filme"),
    path("filmes/", views.lista_filmes, name="lista_filmes"),
    path("filmes-atores/", views.lista_filme_atores, name="lista_filme_atores"),
    path("series/", views.lista_series, name="lista_series"),
    path("episodios/", views.lista_episodios, name="lista_episodios"),
    path("temporadas/", views.lista_temporadas, name="lista_temporadas"),
    path("generos/", views.lista_generos, name="lista_generos"),
    path("pessoas/", views.lista_pessoas, name="lista_pessoas"),
    path("paises/", views.lista_paises, name="lista_paises"),
    path("continentes/", views.lista_continentes, name="lista_continentes"),

    # Autenticação
    path("registrar/", views.registrar, name="registrar"),
    path("login/", auth_views.LoginView.as_view(template_name="app/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="app:index"), name="logout"),

    # Avaliações
    path("filme/<int:filme_id>/avaliar/", views.avaliar_filme, name="avaliar_filme"),
]