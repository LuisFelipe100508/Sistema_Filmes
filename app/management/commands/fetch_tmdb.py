"""
Comando para buscar filmes reais do TMDB: em cartaz, em breve e já lançados
(populares/bem avaliados). Traz elenco com fotos, sinopse, gêneros, diretor,
trailer do YouTube, galeria de imagens e onde assistir em streaming no Brasil.

Uso:
    python manage.py fetch_tmdb
    python manage.py fetch_tmdb --tipo=em_cartaz
    python manage.py fetch_tmdb --tipo=em_breve
    python manage.py fetch_tmdb --tipo=lancados --paginas-lancados=10
    python manage.py fetch_tmdb --paginas=2
    python manage.py fetch_tmdb --limpar
"""
from datetime import datetime, timedelta, date

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.models import Filme, Genero, Pais, Pessoa, FilmeAtor, FilmeImagem, Streaming, FilmeStreaming

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
            choices=["em_cartaz", "em_breve", "lancados", "ambos"],
            default="ambos",
            help="Qual categoria buscar no TMDB",
        )
        parser.add_argument(
            "--paginas",
            type=int,
            default=1,
            help="Páginas de em_cartaz/em_breve a buscar (20 filmes por página)",
        )
        parser.add_argument(
            "--paginas-lancados",
            type=int,
            default=5,
            help="Páginas de filmes já lançados a buscar (20 por página). Padrão: 5",
        )
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Remove filmes importados do TMDB antes de buscar novamente",
        )

    def handle(self, *args, **options):
        api_key = settings.TMDB_API_KEY
        if not api_key:
            raise CommandError(
                "TMDB_API_KEY não configurada. Defina a variável de ambiente antes de rodar."
            )

        if options["limpar"]:
            apagados, _ = Filme.objects.filter(tmdb_id__isnull=False).delete()
            self.stdout.write(self.style.WARNING(f"Removidos {apagados} registros importados do TMDB."))

        tipo = options["tipo"]
        paginas = options["paginas"]
        hoje = date.today()

        if tipo in ("em_cartaz", "ambos"):
            self.stdout.write("Buscando filmes EM CARTAZ no TMDB...")
            limite_min = hoje - timedelta(days=DIAS_TOLERANCIA_CARTAZ)
            limite_max = hoje + timedelta(days=7)
            self._processar_lista(
                "now_playing", "em_cartaz", api_key, paginas, limite_min, limite_max
            )

        if tipo in ("em_breve", "ambos"):
            self.stdout.write("Buscando filmes EM BREVE no TMDB...")
            limite_min = hoje + timedelta(days=1)
            limite_max = hoje + timedelta(days=DIAS_MAX_EM_BREVE)
            self._processar_lista(
                "upcoming", "em_breve", api_key, paginas, limite_min, limite_max
            )

        if tipo in ("lancados", "ambos"):
            self.stdout.write("Buscando filmes JÁ LANÇADOS (populares/bem avaliados) no TMDB...")
            paginas_lancados = options["paginas_lancados"]
            self._processar_lancados(api_key, paginas_lancados, hoje)

        self.stdout.write(self.style.SUCCESS("\nImportação concluída!"))

    def _processar_lista(self, endpoint, status_cartaz, api_key, paginas, limite_min, limite_max):
        total_criados = 0
        total_atualizados = 0
        total_ignorados = 0

        for pagina in range(1, paginas + 1):
            resp = requests.get(
                f"{TMDB_BASE_URL}/movie/{endpoint}",
                params={
                    "api_key": api_key,
                    "language": settings.TMDB_LANGUAGE,
                    "region": settings.TMDB_REGION,
                    "page": pagina,
                },
                timeout=15,
            )
            if resp.status_code != 200:
                self.stderr.write(f"Erro na página {pagina}: HTTP {resp.status_code} - {resp.text[:200]}")
                continue

            resultados = resp.json().get("results", [])
            for item in resultados:
                data_str = item.get("release_date")
                if not data_str:
                    total_ignorados += 1
                    continue
                try:
                    data_lancamento = datetime.strptime(data_str, "%Y-%m-%d").date()
                except ValueError:
                    total_ignorados += 1
                    continue

                if not (limite_min <= data_lancamento <= limite_max):
                    total_ignorados += 1
                    continue

                criado = self._salvar_filme(item, status_cartaz, api_key, data_lancamento)
                if criado:
                    total_criados += 1
                else:
                    total_atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"  -> {status_cartaz}: {total_criados} criados, "
                f"{total_atualizados} atualizados, {total_ignorados} ignorados (fora da janela de datas)"
            )
        )

    def _processar_lancados(self, api_key, paginas, hoje):
        total_criados = 0
        total_atualizados = 0
        total_ignorados = 0

        for endpoint in ["popular", "top_rated"]:
            for pagina in range(1, paginas + 1):
                resp = requests.get(
                    f"{TMDB_BASE_URL}/movie/{endpoint}",
                    params={
                        "api_key": api_key,
                        "language": settings.TMDB_LANGUAGE,
                        "region": settings.TMDB_REGION,
                        "page": pagina,
                    },
                    timeout=15,
                )
                if resp.status_code != 200:
                    self.stderr.write(f"Erro em {endpoint} pág {pagina}: HTTP {resp.status_code}")
                    continue

                resultados = resp.json().get("results", [])
                for item in resultados:
                    data_str = item.get("release_date")
                    if not data_str:
                        total_ignorados += 1
                        continue
                    try:
                        data_lancamento = datetime.strptime(data_str, "%Y-%m-%d").date()
                    except ValueError:
                        total_ignorados += 1
                        continue

                    if data_lancamento > hoje:
                        total_ignorados += 1
                        continue

                    ja_existe_ativo = Filme.objects.filter(
                        tmdb_id=item["id"], status_cartaz__in=["em_cartaz", "em_breve"]
                    ).exists()
                    if ja_existe_ativo:
                        total_ignorados += 1
                        continue

                    criado = self._salvar_filme(item, "lancado", api_key, data_lancamento)
                    if criado:
                        total_criados += 1
                    else:
                        total_atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"  -> lancados: {total_criados} criados, "
                f"{total_atualizados} atualizados, {total_ignorados} ignorados"
            )
        )

    def _salvar_filme(self, item, status_cartaz, api_key, data_lancamento):
        tmdb_id = item["id"]
        nome = item.get("title") or item.get("original_title")
        sinopse = item.get("overview") or ""
        nota = item.get("vote_average")
        poster_path = item.get("poster_path")
        backdrop_path = item.get("backdrop_path")

        duracao_min = 120
        detalhes = self._buscar_detalhes(tmdb_id, api_key)
        if detalhes:
            duracao_min = detalhes.get("runtime") or duracao_min

        filme, criado = Filme.objects.update_or_create(
            tmdb_id=tmdb_id,
            defaults={
                "nome": nome,
                "sinopse": sinopse,
                "nota_avaliacao": round(nota, 1) if nota else None,
                "data_lancamento": data_lancamento,
                "data_estreia_cinema": data_lancamento,
                "duracao": self._minutos_para_duration(duracao_min),
                "poster_url": f"{POSTER_BASE_URL}{poster_path}" if poster_path else None,
                "backdrop_url": f"{BACKDROP_BASE_URL}{backdrop_path}" if backdrop_path else None,
                "status_cartaz": status_cartaz,
            },
        )

        if detalhes and detalhes.get("genres"):
            generos_obj = []
            for g in detalhes["genres"]:
                genero_obj, _ = Genero.objects.get_or_create(nome=g["name"])
                generos_obj.append(genero_obj)
            filme.genero.set(generos_obj)

        if detalhes and detalhes.get("production_countries"):
            paises_obj = []
            for p in detalhes["production_countries"]:
                pais_obj = Pais.objects.filter(nome=p["name"]).first()
                if not pais_obj:
                    from app.models import Continente
                    continente_outro, _ = Continente.objects.get_or_create(nome="Outro")
                    pais_obj = Pais.objects.create(nome=p["name"], continente=continente_outro)
                paises_obj.append(pais_obj)
            filme.pais.set(paises_obj)

        creditos = self._buscar_creditos(tmdb_id, api_key)
        if creditos:
            diretor_info = next(
                (c for c in creditos.get("crew", []) if c.get("job") == "Director"), None
            )
            if diretor_info:
                diretor_obj, _ = Pessoa.objects.get_or_create(nome=diretor_info["name"])
                if diretor_info.get("profile_path") and not diretor_obj.foto_url:
                    diretor_obj.foto_url = f"{PROFILE_BASE_URL}{diretor_info['profile_path']}"
                    diretor_obj.save()
                filme.diretor = diretor_obj
                filme.save()

            elenco_tmdb = creditos.get("cast", [])[:10]
            for ator_info in elenco_tmdb:
                ator_obj, _ = Pessoa.objects.get_or_create(nome=ator_info["name"])
                if ator_info.get("profile_path") and not ator_obj.foto_url:
                    ator_obj.foto_url = f"{PROFILE_BASE_URL}{ator_info['profile_path']}"
                    ator_obj.save()
                FilmeAtor.objects.update_or_create(
                    filme=filme,
                    ator=ator_obj,
                    defaults={"personagem": ator_info.get("character", "")},
                )

        # Trailer do YouTube
        videos_resp = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}/videos",
            params={"api_key": api_key, "language": settings.TMDB_LANGUAGE},
            timeout=15,
        )
        if videos_resp.status_code == 200:
            videos = videos_resp.json().get("results", [])
            trailer = next(
                (v for v in videos if v["site"] == "YouTube" and v["type"] == "Trailer" and v.get("official")),
                None,
            ) or next(
                (v for v in videos if v["site"] == "YouTube" and v["type"] == "Trailer"),
                None,
            )
            if not trailer:
                videos_resp_en = requests.get(
                    f"{TMDB_BASE_URL}/movie/{tmdb_id}/videos",
                    params={"api_key": api_key, "language": "en-US"},
                    timeout=15,
                )
                if videos_resp_en.status_code == 200:
                    videos_en = videos_resp_en.json().get("results", [])
                    trailer = next(
                        (v for v in videos_en if v["site"] == "YouTube" and v["type"] == "Trailer"),
                        None,
                    )
            if trailer:
                filme.trailer_key = trailer["key"]
                filme.save()

        # Galeria de imagens (backdrops) para slideshow de fundo
        images_resp = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}/images",
            params={"api_key": api_key},
            timeout=15,
        )
        if images_resp.status_code == 200:
            backdrops = images_resp.json().get("backdrops", [])[:5]
            FilmeImagem.objects.filter(filme=filme).delete()
            for i, img in enumerate(backdrops):
                FilmeImagem.objects.create(
                    filme=filme,
                    url=f"{BACKDROP_BASE_URL}{img['file_path']}",
                    ordem=i,
                )

        # Onde assistir (streaming) - dados reais por região (Brasil)
        providers_resp = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}/watch/providers",
            params={"api_key": api_key},
            timeout=15,
        )
        if providers_resp.status_code == 200:
            br_data = providers_resp.json().get("results", {}).get("BR", {})
            mapeamento_tipo = {
                "flatrate": "assinatura",
                "rent": "aluguel",
                "buy": "compra",
            }
            for chave_tmdb, tipo_local in mapeamento_tipo.items():
                for p_item in br_data.get(chave_tmdb, []):
                    nome_provider = p_item["provider_name"]
                    if nome_provider not in PROVEDORES_RELEVANTES:
                        continue
                    streaming_obj, _ = Streaming.objects.get_or_create(
                        tmdb_provider_id=p_item["provider_id"],
                        defaults={
                            "nome": nome_provider,
                            "logo_url": f"{LOGO_BASE_URL}{p_item['logo_path']}",
                        },
                    )
                    FilmeStreaming.objects.get_or_create(
                        filme=filme, streaming=streaming_obj, tipo=tipo_local
                    )

        return criado

    def _buscar_detalhes(self, tmdb_id, api_key):
        resp = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}",
            params={"api_key": api_key, "language": settings.TMDB_LANGUAGE},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
        return None

    def _buscar_creditos(self, tmdb_id, api_key):
        resp = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}/credits",
            params={"api_key": api_key, "language": settings.TMDB_LANGUAGE},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
        return None

    @staticmethod
    def _minutos_para_duration(minutos):
        return timedelta(minutes=minutos)