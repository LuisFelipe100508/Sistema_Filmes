from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("buscar/", views.buscar, name="buscar"),
    path("filme/<int:filme_id>/", views.detalhe_filme, name="detalhe_filme"),
    path("filmes/", views.lista_filmes, name="lista_filmes"),

    path("generos/", views.generos, name="generos"),
    path("genero/<int:genero_id>/", views.filmes_por_genero, name="filmes_por_genero"),

    path("ranking/", views.ranking, name="ranking"),

    path("favoritos/", views.meus_favoritos, name="meus_favoritos"),
    path("filme/<int:filme_id>/favoritar/", views.favoritar_filme, name="favoritar_filme"),

    # Autenticação e acesso de visitante
    path("registrar/", views.registrar, name="registrar"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="app/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("visitante/", views.entrar_visitante, name="entrar_visitante"),
    path("logout/", auth_views.LogoutView.as_view(next_page="app:login"), name="logout"),

    # Avaliações
    path("filme/<int:filme_id>/avaliar/", views.avaliar_filme, name="avaliar_filme"),
]