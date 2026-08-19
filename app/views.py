from django.shortcuts import render
from .models import (
    Continente,
    Pais,
    Genero,
    Pessoa,
    Filme,
    FilmeAtor,
    Serie,
    Temporada,
    Episodio,
    SerieEpisodio,
)


def index(request):
    """Página inicial com links para todas as listagens."""
    return render(request, "app/index.html")


def lista_filmes(request):
    filmes = Filme.objects.prefetch_related("genero", "pais", "elenco__ator").select_related("diretor")
    return render(request, "app/lista_filmes.html", {"filmes": filmes})


def lista_series(request):
    series = Serie.objects.prefetch_related("genero", "pais", "temporadas").select_related("diretor")
    return render(request, "app/lista_series.html", {"series": series})


def lista_episodios(request):
    dados = SerieEpisodio.objects.select_related("serie", "temporada", "episodio").all()
    return render(request, "app/lista_episodios.html", {"dados": dados})


def lista_generos(request):
    generos = Genero.objects.all()
    return render(request, "app/lista_generos.html", {"generos": generos})


def lista_pessoas(request):
    pessoas = Pessoa.objects.select_related("nacionalidade").all()
    return render(request, "app/lista_pessoas.html", {"pessoas": pessoas})


def lista_paises(request):
    paises = Pais.objects.select_related("continente").all()
    return render(request, "app/lista_paises.html", {"paises": paises})


def lista_continentes(request):
    continentes = Continente.objects.all()
    return render(request, "app/lista_continentes.html", {"continentes": continentes})


def lista_temporadas(request):
    temporadas = Temporada.objects.select_related("serie").all()
    return render(request, "app/lista_temporadas.html", {"temporadas": temporadas})


def lista_filme_atores(request):
    relacoes = FilmeAtor.objects.select_related("filme", "ator").all()
    return render(request, "app/lista_filme_atores.html", {"relacoes": relacoes})