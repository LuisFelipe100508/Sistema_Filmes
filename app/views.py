from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404

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
    AvaliacaoUsuario,
    Sessao,
)


def index(request):
    """Home dinâmica: mostra filmes em cartaz e em breve, com poster e nota."""
    em_cartaz = Filme.objects.filter(status_cartaz="em_cartaz").order_by("-nota_avaliacao")[:8]
    em_breve = Filme.objects.filter(status_cartaz="em_breve").order_by("data_estreia_cinema")[:8]
    return render(request, "app/index.html", {
        "em_cartaz": em_cartaz,
        "em_breve": em_breve,
    })


def detalhe_filme(request, filme_id):
    filme = get_object_or_404(
        Filme.objects.prefetch_related(
            "genero", "pais", "elenco__ator", "sessoes__cinema", "avaliacoes_usuarios__usuario"
        ).select_related("diretor"),
        id=filme_id,
    )
    avaliacoes = filme.avaliacoes_usuarios.all()
    ja_avaliou = False
    if request.user.is_authenticated:
        ja_avaliou = avaliacoes.filter(usuario=request.user).exists()

    media_usuarios = None
    if avaliacoes.exists():
        total = sum(a.nota for a in avaliacoes)
        media_usuarios = round(total / avaliacoes.count(), 1)

    return render(request, "app/detalhe_filme.html", {
        "filme": filme,
        "avaliacoes": avaliacoes,
        "ja_avaliou": ja_avaliou,
        "media_usuarios": media_usuarios,
        "sessoes_ativas": [s for s in filme.sessoes.all() if s.em_cartaz_agora],
    })


def lista_filmes(request):
    filmes = Filme.objects.prefetch_related("genero", "pais", "elenco__ator").select_related("diretor")
    return render(request, "app/lista_filmes.html", {"filmes": filmes})


def lista_filme_atores(request):
    relacoes = FilmeAtor.objects.select_related("filme", "ator").all()
    return render(request, "app/lista_filme_atores.html", {"relacoes": relacoes})


def lista_series(request):
    series = Serie.objects.prefetch_related("genero", "pais", "temporadas").select_related("diretor")
    return render(request, "app/lista_series.html", {"series": series})


def lista_temporadas(request):
    temporadas = Temporada.objects.select_related("serie").all()
    return render(request, "app/lista_temporadas.html", {"temporadas": temporadas})


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


def registrar(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Bem-vindo(a), {user.username}! Sua conta foi criada.")
            return redirect("app:index")
    else:
        form = UserCreationForm()
    return render(request, "app/registrar.html", {"form": form})


@login_required
def avaliar_filme(request, filme_id):
    filme = get_object_or_404(Filme, id=filme_id)

    if request.method == "POST":
        nota = request.POST.get("nota")
        comentario = request.POST.get("comentario", "").strip()

        if nota and nota.isdigit() and 1 <= int(nota) <= 5:
            AvaliacaoUsuario.objects.update_or_create(
                filme=filme,
                usuario=request.user,
                defaults={"nota": int(nota), "comentario": comentario},
            )
            messages.success(request, "Sua avaliação foi registrada!")
        else:
            messages.error(request, "Nota inválida. Escolha de 1 a 5 estrelas.")

    return redirect("app:detalhe_filme", filme_id=filme.id)