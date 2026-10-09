from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Filme, Genero, AvaliacaoUsuario, Favorito


def _ids_favoritos(request):
    """IDs dos filmes favoritados pelo usuário logado (vazio para visitantes)."""
    if request.user.is_authenticated:
        return set(
            Favorito.objects.filter(usuario=request.user).values_list("filme_id", flat=True)
        )
    return set()


def index(request):
    """Home dinâmica: mostra filmes em cartaz e em breve, com poster e nota."""
    em_cartaz = Filme.objects.filter(status_cartaz="em_cartaz").order_by("-nota_avaliacao")[:8]
    em_breve = Filme.objects.filter(status_cartaz="em_breve").order_by("data_estreia_cinema")[:8]

    return render(request, "app/index.html", {
        "em_cartaz": em_cartaz,
        "em_breve": em_breve,
        "favoritos_ids": _ids_favoritos(request),
    })


def buscar(request):
    termo = request.GET.get("q", "").strip()
    resultados = []
    if termo:
        resultados = Filme.objects.filter(
            Q(nome__icontains=termo) | Q(sinopse__icontains=termo)
        ).distinct()[:40]

    return render(request, "app/buscar.html", {
        "termo": termo,
        "resultados": resultados,
        "favoritos_ids": _ids_favoritos(request),
    })


def detalhe_filme(request, filme_id):
    filme = get_object_or_404(
        Filme.objects.prefetch_related(
            "genero", "pais", "elenco__ator", "sessoes__cinema",
            "avaliacoes_usuarios__usuario", "streamings__streaming", "galeria"
        ).select_related("diretor"),
        id=filme_id,
    )
    avaliacoes = filme.avaliacoes_usuarios.all()
    ja_avaliou = False
    ja_favoritou = False
    if request.user.is_authenticated:
        ja_avaliou = avaliacoes.filter(usuario=request.user).exists()
        ja_favoritou = Favorito.objects.filter(usuario=request.user, filme=filme).exists()

    media_usuarios = None
    if avaliacoes.exists():
        total = sum(a.nota for a in avaliacoes)
        media_usuarios = round(total / avaliacoes.count(), 1)

    return render(request, "app/detalhe_filme.html", {
        "filme": filme,
        "elenco": filme.elenco.select_related("ator").all(),
        "avaliacoes": avaliacoes,
        "ja_avaliou": ja_avaliou,
        "ja_favoritou": ja_favoritou,
        "media_usuarios": media_usuarios,
        "sessoes_ativas": [s for s in filme.sessoes.all() if s.em_cartaz_agora],
    })


def lista_filmes(request):
    filmes = Filme.objects.prefetch_related("genero", "pais").select_related("diretor")
    return render(request, "app/lista_filmes.html", {
        "filmes": filmes,
        "favoritos_ids": _ids_favoritos(request),
    })


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
        "favoritos_ids": _ids_favoritos(request),
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


@login_required
def meus_favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related("filme")
    return render(request, "app/favoritos.html", {"favoritos": favoritos})


@login_required
def favoritar_filme(request, filme_id):
    """Alterna (toggle) o favorito: se já tiver, remove; se não tiver, adiciona."""
    filme = get_object_or_404(Filme, id=filme_id)
    favorito, criado = Favorito.objects.get_or_create(usuario=request.user, filme=filme)

    if not criado:
        favorito.delete()
        favoritado = False
    else:
        favoritado = True

    # Se a requisição veio via AJAX (fetch), responde em JSON pro coração mudar sem recarregar a página
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"favoritado": favoritado})

    # Fallback sem JS: volta pra página de onde veio
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "app:index"
    return redirect(next_url)


def registrar(request):
    if request.user.is_authenticated:
        return redirect("app:index")

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


@require_POST
def entrar_visitante(request):
    """
    Libera a navegação sem conta. Guarda só uma marca na sessão do servidor
    (não cria usuário e não concede nenhuma permissão). A sessão do visitante
    expira quando o navegador é fechado.
    """
    if not request.user.is_authenticated:
        request.session["visitante"] = True
        request.session.set_expiry(0)

    # Só aceita voltar para um endereço do próprio site (evita redirecionamento malicioso)
    destino = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        destino = "app:index"
    return redirect(destino)


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