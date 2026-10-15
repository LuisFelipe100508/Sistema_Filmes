"""
Importa filmes do TMDB: em cartaz, em breve e já lançados.
Traz elenco com foto, sinopse, gêneros, diretor, trailer, galeria e onde assistir (Brasil).

Uso:
    python manage.py fetch_tmdb --tipo=atualizar        (rotina diária: em cartaz + em breve)
    python manage.py fetch_tmdb --tipo=em_cartaz
    python manage.py fetch_tmdb --tipo=em_breve
    python manage.py fetch_tmdb --tipo=lancados --paginas-lancados=10
    python manage.py fetch_tmdb                         (tudo: cartaz + breve + lançados)
    python manage.py fetch_tmdb --limpar --forcar       (apaga os filmes importados; cuidado!)
"""
import time
from datetime import date, datetime, timedelta

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.models import (
    AvaliacaoUsuario,
    Continente,
    Favorito,
    Filme,
    FilmeAtor,
    FilmeImagem,
    FilmeStreaming,
    Genero,
    Pais,
    Pessoa,
    Streaming,
)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"
PROFILE_BASE_URL = "https://image.tmdb.org/t/p/w185"
LOGO_BASE_URL = "https://image.tmdb.org/t/p/w92"

DIAS_TOLERANCIA_CARTAZ = 45
DIAS_MAX_EM_BREVE = 365

PROVEDORES_RELEVANTES = {
    "Netflix", "Amazon Prime Video", "Disney Plus", "HBO Max", "Max",
    "Apple TV", "Apple TV Plus", "Paramount Plus", "Globoplay", "Star Plus",
    "Google Play Movies", "YouTube",
}


class Command(BaseCommand):
    help = "Busca filmes em cartaz, em breve e já lançados na API do TMDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tipo",
            choices=["em_cartaz", "em_breve", "atualizar", "lancados", "ambos"],
            default="ambos",
            help="'atualizar' = em cartaz + em breve (rotina diária); 'ambos' = tudo",
        )
        parser.add_argument(
            "--paginas", type=int, default=1,
            help="Páginas de em cartaz/em breve (20 filmes por página)",
        )
        parser.add_argument(
            "--paginas-lancados", type=int, default=5,
            help="Páginas de filmes já lançados (20 por página). Padrão: 5",
        )
        parser.add_argument(
            "--limpar", action="store_true",
            help="Remove os filmes importados do TMDB antes de buscar de novo",
        )
        parser.add_argument(
            "--forcar", action="store_true",
            help="Confirma o --limpar mesmo havendo favoritos/avaliações de usuários",
        )

    def handle(self, *args, **options):
        api_key = settings.TMDB_API_KEY
        if not api_key:
            raise CommandError(
                "TMDB_API_KEY não configurada. Defina a variável de ambiente antes de rodar."
            )

        if options["limpar"]:
            self._limpar(options["forcar"])

        tipo = options["tipo"]
        paginas = options["paginas"]
        hoje = date.today()

        if tipo in ("em_cartaz", "atualizar", "ambos"):
            self.stdout.write("Buscando filmes EM CARTAZ no TMDB...")
            vistos = self._processar_lista(
                "now_playing", "em_cartaz", api_key, paginas,
                hoje - timedelta(days=DIAS_TOLERANCIA_CARTAZ),
                hoje + timedelta(days=7),
            )
            # Só rebaixa se a API respondeu de verdade (lista não vazia)
            if vistos:
                saiu_de_cartaz = Filme.objects.filter(
                    status_cartaz="em_cartaz", tmdb_id__isnull=False
                ).exclude(tmdb_id__in=vistos).update(status_cartaz="lancado")
                self.stdout.write(f"  -> {saiu_de_cartaz} filme(s) saíram de cartaz e foram para 'Já lançados'")

        if tipo in ("em_breve", "atualizar", "ambos"):
            self.stdout.write("Buscando filmes EM BREVE no TMDB...")
            self._processar_lista(
                "upcoming", "em_breve", api_key, paginas,
                hoje + timedelta(days=1),
                hoje + timedelta(days=DIAS_MAX_EM_BREVE),
            )

        if tipo in ("atualizar", "ambos"):
            # "Em breve" cuja data de estreia já passou e que não entrou em cartaz
            estreados = Filme.objects.filter(
                status_cartaz="em_breve", tmdb_id__isnull=False,
                data_estreia_cinema__lte=hoje,
            ).update(status_cartaz="lancado")
            if estreados:
                self.stdout.write(f"  -> {estreados} estreia(s) já passaram e foram para 'Já lançados'")

        if tipo in ("lancados", "ambos"):
            self.stdout.write("Buscando filmes JÁ LANÇADOS (populares/bem avaliados) no TMDB...")
            self._processar_lancados(api_key, options["paginas_lancados"], hoje)

        self.stdout.write(self.style.SUCCESS("\nImportação concluída!"))

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _limpar(self, forcar):
        if not forcar and (Favorito.objects.exists() or AvaliacaoUsuario.objects.exists()):
            raise CommandError(
                "Existem favoritos/avaliações de usuários e o --limpar apagaria tudo isso "
                "em cascata. Se tiver certeza, rode de novo com --forcar."
            )
        apagados, _ = Filme.objects.filter(tmdb_id__isnull=False).delete()
        self.stdout.write(self.style.WARNING(f"Removidos {apagados} registros importados do TMDB."))

    def _get(self, url, params):
        """GET com algumas tentativas, para não quebrar a rotina por uma falha passageira."""
        for tentativa in range(3):
            try:
                resp = requests.get(url, params=params, timeout=15)
            except requests.RequestException:
                time.sleep(2 * (tentativa + 1))
                continue
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(2 * (tentativa + 1))
                continue
            return resp
        return None

    @staticmethod
    def _data(item):
        texto = item.get("release_date")
        if not texto:
            return None
        try:
            return datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _minutos_para_duration(minutos):
        return timedelta(minutes=minutos)

    # ------------------------------------------------------------------
    # Listas
    # ------------------------------------------------------------------
    def _processar_lista(self, endpoint, status_cartaz, api_key, paginas, limite_min, limite_max):
        criados = atualizados = ignorados = 0
        vistos = set()

        for pagina in range(1, paginas + 1):
            resp = self._get(f"{TMDB_BASE_URL}/movie/{endpoint}", {
                "api_key": api_key,
                "language": settings.TMDB_LANGUAGE,
                "region": settings.TMDB_REGION,
                "page": pagina,
            })
            if resp is None or resp.status_code != 200:
                self.stderr.write(f"Erro ao buscar a página {pagina} de {endpoint}.")
                continue

            for item in resp.json().get("results", []):
                data_lancamento = self._data(item)
                if not data_lancamento or not (limite_min <= data_lancamento <= limite_max):
                    ignorados += 1
                    continue

                if self._salvar_filme(item, status_cartaz, api_key, data_lancamento):
                    criados += 1
                else:
                    atualizados += 1
                vistos.add(item["id"])

        self.stdout.write(self.style.SUCCESS(
            f"  -> {status_cartaz}: {criados} criados, {atualizados} atualizados, "
            f"{ignorados} ignorados (fora da janela de datas)"
        ))
        return vistos

    def _processar_lancados(self, api_key, paginas, hoje):
        criados = atualizados = ignorados = 0

        for endpoint in ("popular", "top_rated"):
            for pagina in range(1, paginas + 1):
                resp = self._get(f"{TMDB_BASE_URL}/movie/{endpoint}", {
                    "api_key": api_key,
                    "language": settings.TMDB_LANGUAGE,
                    "region": settings.TMDB_REGION,
                    "page": pagina,
                })
                if resp is None or resp.status_code != 200:
                    self.stderr.write(f"Erro em {endpoint}, página {pagina}.")
                    continue

                for item in resp.json().get("results", []):
                    data_lancamento = self._data(item)
                    if not data_lancamento or data_lancamento > hoje:
                        ignorados += 1
                        continue

                    # Não rebaixa um filme que está em cartaz/em breve
                    if Filme.objects.filter(
                        tmdb_id=item["id"], status_cartaz__in=["em_cartaz", "em_breve"]
                    ).exists():
                        ignorados += 1
                        continue

                    if self._salvar_filme(item, "lancado", api_key, data_lancamento):
                        criados += 1
                    else:
                        atualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f"  -> lancados: {criados} criados, {atualizados} atualizados, {ignorados} ignorados"
        ))

    # ------------------------------------------------------------------
    # Um filme completo
    # ------------------------------------------------------------------
    def _salvar_filme(self, item, status_cartaz, api_key, data_lancamento):
        tmdb_id = item["id"]
        nota = item.get("vote_average")
        poster_path = item.get("poster_path")
        backdrop_path = item.get("backdrop_path")

        duracao_min = 120
        detalhes = self._json(f"{TMDB_BASE_URL}/movie/{tmdb_id}", {
            "api_key": api_key, "language": settings.TMDB_LANGUAGE,
        })
        if detalhes:
            duracao_min = detalhes.get("runtime") or duracao_min

        filme, criado = Filme.objects.update_or_create(
            tmdb_id=tmdb_id,
            defaults={
                "nome": item.get("title") or item.get("original_title"),
                "sinopse": item.get("overview") or "",
                "nota_avaliacao": round(nota, 1) if nota else None,
                "data_lancamento": data_lancamento,
                "data_estreia_cinema": data_lancamento,
                "duracao": self._minutos_para_duration(duracao_min),
                "poster_url": f"{POSTER_BASE_URL}{poster_path}" if poster_path else None,
                "backdrop_url": f"{BACKDROP_BASE_URL}{backdrop_path}" if backdrop_path else None,
                "status_cartaz": status_cartaz,
            },
        )

        # Gêneros
        if detalhes and detalhes.get("genres"):
            filme.genero.set([
                Genero.objects.get_or_create(nome=g["name"])[0] for g in detalhes["genres"]
            ])

        # Países de produção
        if detalhes and detalhes.get("production_countries"):
            paises = []
            for p in detalhes["production_countries"]:
                pais = Pais.objects.filter(nome=p["name"]).first()
                if not pais:
                    outro, _ = Continente.objects.get_or_create(nome="Outro")
                    pais = Pais.objects.create(nome=p["name"], continente=outro)
                paises.append(pais)
            filme.pais.set(paises)

        # Diretor e elenco
        creditos = self._json(f"{TMDB_BASE_URL}/movie/{tmdb_id}/credits", {
            "api_key": api_key, "language": settings.TMDB_LANGUAGE,
        })
        if creditos:
            diretor_info = next(
                (c for c in creditos.get("crew", []) if c.get("job") == "Director"), None
            )
            if diretor_info:
                diretor, _ = Pessoa.objects.get_or_create(nome=diretor_info["name"])
                if diretor_info.get("profile_path") and not diretor.foto_url:
                    diretor.foto_url = f"{PROFILE_BASE_URL}{diretor_info['profile_path']}"
                    diretor.save()
                filme.diretor = diretor
                filme.save()

            for ator_info in creditos.get("cast", [])[:10]:
                ator, _ = Pessoa.objects.get_or_create(nome=ator_info["name"])
                if ator_info.get("profile_path") and not ator.foto_url:
                    ator.foto_url = f"{PROFILE_BASE_URL}{ator_info['profile_path']}"
                    ator.save()
                FilmeAtor.objects.update_or_create(
                    filme=filme, ator=ator,
                    defaults={"personagem": ator_info.get("character", "")},
                )

        # Trailer do YouTube (tenta em português e, se não houver, em inglês)
        trailer = None
        for idioma in (settings.TMDB_LANGUAGE, "en-US"):
            dados = self._json(f"{TMDB_BASE_URL}/movie/{tmdb_id}/videos", {
                "api_key": api_key, "language": idioma,
            })
            videos = (dados or {}).get("results", [])
            trailer = next(
                (v for v in videos
                 if v["site"] == "YouTube" and v["type"] == "Trailer" and v.get("official")),
                None,
            ) or next(
                (v for v in videos if v["site"] == "YouTube" and v["type"] == "Trailer"),
                None,
            )
            if trailer:
                break
        if trailer:
            filme.trailer_key = trailer["key"]
            filme.save()

        # Galeria de imagens (slideshow de fundo)
        imagens = self._json(f"{TMDB_BASE_URL}/movie/{tmdb_id}/images", {"api_key": api_key})
        if imagens:
            FilmeImagem.objects.filter(filme=filme).delete()
            for i, img in enumerate(imagens.get("backdrops", [])[:5]):
                FilmeImagem.objects.create(
                    filme=filme, url=f"{BACKDROP_BASE_URL}{img['file_path']}", ordem=i,
                )

        # Onde assistir em streaming (Brasil)
        provedores = self._json(f"{TMDB_BASE_URL}/movie/{tmdb_id}/watch/providers", {
            "api_key": api_key,
        })
        if provedores:
            br = provedores.get("results", {}).get("BR", {})
            for chave_tmdb, tipo_local in (
                ("flatrate", "assinatura"), ("rent", "aluguel"), ("buy", "compra"),
            ):
                for p_item in br.get(chave_tmdb, []):
                    if p_item["provider_name"] not in PROVEDORES_RELEVANTES:
                        continue
                    streaming, _ = Streaming.objects.get_or_create(
                        tmdb_provider_id=p_item["provider_id"],
                        defaults={
                            "nome": p_item["provider_name"],
                            "logo_url": f"{LOGO_BASE_URL}{p_item['logo_path']}",
                        },
                    )
                    FilmeStreaming.objects.get_or_create(
                        filme=filme, streaming=streaming, tipo=tipo_local
                    )

        return criado

    def _json(self, url, params):
        resp = self._get(url, params)
        if resp is not None and resp.status_code == 200:
            return resp.json()
        return None