from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404

from .models import Filme, Genero, AvaliacaoUsuario


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
            "genero", "pais", "elenco__ator", "sessoes__cinema",
            "avaliacoes_usuarios__usuario", "streamings__streaming"
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
        "elenco": filme.elenco.select_related("ator").all(),
        "avaliacoes": avaliacoes,
        "ja_avaliou": ja_avaliou,
        "media_usuarios": media_usuarios,
        "sessoes_ativas": [s for s in filme.sessoes.all() if s.em_cartaz_agora],
    })


def lista_filmes(request):
    filmes = Filme.objects.prefetch_related("genero", "pais").select_related("diretor")
    return render(request, "app/lista_filmes.html", {"filmes": filmes})


def generos(request):
    lista_generos = Genero.objects.all().order_by("nome")
    return render(request, "app/generos.html", {"generos": lista_generos})


def filmes_por_genero(request, genero_id):
    genero = get_object_or_404(Genero, id=genero_id)
    filmes_em_cartaz = Filme.objects.filter(genero=genero, status_cartaz="em_cartaz").order_by("-nota_avaliacao")
    filmes_em_breve = Filme.objects.filter(genero=genero, status_cartaz="em_breve").order_by("data_estreia_cinema")
    filmes_lancados = Filme.objects.filter(genero=genero, status_cartaz="lancado").order_by("-nota_avaliacao")

    return render(request, "app/filmes_por_genero.html", {
        "genero": genero,
        "filmes_em_cartaz": filmes_em_cartaz,
        "filmes_em_breve": filmes_em_breve,
        "filmes_lancados": filmes_lancados,
    })


def ranking(request):
    genero_id = request.GET.get("genero")
    filmes = Filme.objects.exclude(nota_avaliacao__isnull=True)

    if genero_id:
        filmes = filmes.filter(genero__id=genero_id)

    filmes = filmes.order_by("-nota_avaliacao")[:30]
    lista_generos = Genero.objects.all().order_by("nome")

    return render(request, "app/ranking.html", {
        "filmes": filmes,
        "generos": lista_generos,
        "genero_selecionado": int(genero_id) if genero_id else None,
    })


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

    if filme.status_cartaz == "em_breve":
        messages.error(request, "Este filme ainda não estreou — você poderá avaliá-lo após o lançamento.")
        return redirect("app:detalhe_filme", filme_id=filme.id)

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