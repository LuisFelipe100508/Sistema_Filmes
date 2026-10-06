"""
Comando para buscar filmes reais do TMDB (Em Cartaz e Em Breve)
e preencher automaticamente o catálogo local.

Uso:
    python manage.py fetch_tmdb
    python manage.py fetch_tmdb --tipo=em_cartaz
    python manage.py fetch_tmdb --tipo=em_breve
    python manage.py fetch_tmdb --paginas=2
    python manage.py fetch_tmdb --limpar   (remove filmes importados do TMDB antes de buscar de novo)
"""
from datetime import datetime, timedelta, date

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.models import Filme, Genero, Pais, Pessoa

TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"
PROFILE_BASE_URL = "https://image.tmdb.org/t/p/w185"
LOGO_BASE_URL = "https://image.tmdb.org/t/p/w92"

# Lista de provedores que queremos manter (evita poluir com serviços obscuros)
PROVEDORES_RELEVANTES = {
    "Netflix", "Amazon Prime Video", "Disney Plus", "HBO Max", "Max",
    "Apple TV", "Apple TV Plus", "Paramount Plus", "Globoplay", "Star Plus",
    "Google Play Movies", "YouTube",
}

# Filmes "em cartaz" só são aceitos se estrearam nos últimos N dias
# ou nos próximos 7 dias (evita re-lançamentos antigos tipo "Vingadores 2019").
DIAS_TOLERANCIA_CARTAZ = 45

# Filmes "em breve" só são aceitos se a estreia for estritamente no futuro
# e dentro de ~1 ano (evita lixo de filmes antigos vindo da API).
DIAS_MAX_EM_BREVE = 365


class Command(BaseCommand):
    help = "Busca filmes em cartaz e em breve na API do TMDB e popula o banco local"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tipo",
            choices=["em_cartaz", "em_breve", "ambos"],
            default="ambos",
            help="Qual categoria buscar no TMDB",
        )
        parser.add_argument(
            "--paginas",
            type=int,
            default=1,
            help="Quantas páginas de resultados buscar (20 filmes por página)",
        )
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Remove filmes importados do TMDB antes de buscar novamente (evita lixo acumulado)",
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

                # Filtro real pela data - ignora re-lançamentos antigos e lixo da API
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

                # Diretor (busca nos créditos)
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

            # Elenco - pega os 10 primeiros atores do cast (já vem ordenado por relevância)
            from app.models import FilmeAtor
            elenco_tmdb = creditos.get("cast", [])[:10]
            for ordem, ator_info in enumerate(elenco_tmdb):
                ator_obj, _ = Pessoa.objects.get_or_create(nome=ator_info["name"])
                if ator_info.get("profile_path") and not ator_obj.foto_url:
                    ator_obj.foto_url = f"{PROFILE_BASE_URL}{ator_info['profile_path']}"
                    ator_obj.save()
                FilmeAtor.objects.update_or_create(
                    filme=filme,
                    ator=ator_obj,
                    defaults={"personagem": ator_info.get("character", "")},
                )
            from app.models import Streaming, FilmeStreaming
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
                for item in br_data.get(chave_tmdb, []):
                    nome_provider = item["provider_name"]
                    if nome_provider not in PROVEDORES_RELEVANTES:
                        continue
                    streaming_obj, _ = Streaming.objects.get_or_create(
                        tmdb_provider_id=item["provider_id"],
                        defaults={
                            "nome": nome_provider,
                            "logo_url": f"{LOGO_BASE_URL}{item['logo_path']}",
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