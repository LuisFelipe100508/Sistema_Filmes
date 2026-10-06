from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("filme/<int:filme_id>/", views.detalhe_filme, name="detalhe_filme"),
    path("filmes/", views.lista_filmes, name="lista_filmes"),

    # Autenticação
    path("registrar/", views.registrar, name="registrar"),
    path("login/", auth_views.LoginView.as_view(template_name="app/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="app:index"), name="logout"),

    # Avaliações
    path("filme/<int:filme_id>/avaliar/", views.avaliar_filme, name="avaliar_filme"),
]