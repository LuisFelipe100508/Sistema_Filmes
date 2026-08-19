from datetime import date, timedelta
from django.core.management.base import BaseCommand
from app.models import (
    Continente, Pais, Genero, Pessoa, Filme, FilmeAtor,
    Serie, Temporada, Episodio, SerieEpisodio,
)


class Command(BaseCommand):
    help = "Popula o banco com dados completos de exemplo (RF01-RF10)"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando o povoamento do banco de dados...")

        # ---------------------------------------------------------
        # RF10 - Continentes
        # ---------------------------------------------------------
        continentes_nomes = ["América do Norte", "América do Sul", "Europa", "Ásia", "Oceania"]
        continentes = {}
        for nome in continentes_nomes:
            obj, _ = Continente.objects.get_or_create(nome=nome)
            continentes[nome] = obj
        self.stdout.write(self.style.SUCCESS(f"Continentes: {len(continentes)}"))

        # ---------------------------------------------------------
        # RF09 - Países
        # ---------------------------------------------------------
        paises_data = [
            ("Estados Unidos", "América do Norte"),
            ("Brasil", "América do Sul"),
            ("Reino Unido", "Europa"),
            ("Coreia do Sul", "Ásia"),
            ("Austrália", "Oceania"),
            ("França", "Europa"),
            ("Grécia", "Europa"),
        ]
        paises = {}
        for nome, continente in paises_data:
            obj, _ = Pais.objects.get_or_create(
                nome=nome, defaults={"continente": continentes[continente]}
            )
            paises[nome] = obj
        self.stdout.write(self.style.SUCCESS(f"Países: {len(paises)}"))

        # ---------------------------------------------------------
        # RF03 - Gêneros
        # ---------------------------------------------------------
        generos_nomes = [
            "Ação", "Romance", "Suspense", "Ficção Científica", 
            "Drama", "Comédia", "Documentário", "Terror"
        ]
        generos = {}
        for nome in generos_nomes:
            obj, _ = Genero.objects.get_or_create(nome=nome)
            generos[nome] = obj
        self.stdout.write(self.style.SUCCESS(f"Gêneros: {len(generos)}"))

        # ---------------------------------------------------------
        # RF07 - Pessoas (Atores e Diretores)
        # ---------------------------------------------------------
        pessoas_data = [
            ("Christopher Nolan", "https://christophernolan.com", "@christophernolan", "ChristopherNolanPage", "@cnolan", "Reino Unido"),
            ("Walter Salles", "https://waltersalles.com", "@waltersalles", "WalterSallesOficial", "@waltersalles", "Brasil"),
            ("Bong Joon-ho", "https://bongjoonho.com", "@bongjoonho", "BongJoonHo", "@bongjoonho", "Coreia do Sul"),
            ("Yorgos Lanthimos", "https://lanthimos.com", "@lanthimos", "YorgosLanthimos", "@lanthimos", "Grécia"),
            ("Hwang Dong-hyuk", "https://hwangdonghyuk.com", "@hwangdonghyuk", "HwangDongHyuk", "@hwangdonghyuk", "Coreia do Sul"),
            ("Matt Duffer", "https://dufferbrothers.com", "@mattduffer", "DufferBrothers", "@dufferbros", "Estados Unidos"),
            ("Peter Morgan", "https://petermorgan.com", "@petermorgan", "PeterMorganOfficial", "@petermorgan", "Reino Unido"),
            ("Phoebe Waller-Bridge", "https://phoebewallerbridge.com", "@pwallerbridge", "PhoebeWallerBridge", "@pwallerbridge", "Reino Unido"),
            ("Matthew McConaughey", "https://mcconaughey.com", "@officiallymcconaughey", "MatthewMcConaughey", "@McConaughey", "Estados Unidos"),
            ("Leonardo DiCaprio", "https://leonardodicaprio.com", "@leonardodicaprio", "LeoDiCaprio", "@LeoDiCaprio", "Estados Unidos"),
            ("Fernanda Torres", "https://fernandatorres.com.br", "@fernandatorresoficial", "FernandaTorres", "@FeTorres", "Brasil"),
            ("Wagner Moura", "https://wagnermoura.com", "@wagnermoura", "WagnerMouraOficial", "@wagnermoura", "Brasil"),
            ("Emma Stone", "https://emmastone.com", "@emmastone", "EmmaStoneOfficial", "@emma_stone", "Estados Unidos"),
            ("Millie Bobby Brown", "https://milliebobbybrown.com", "@milliebobbybrown", "MillieBobbyBrown", "@MillieBBrown", "Reino Unido"),
            ("Winona Ryder", "https://winonaryder.com", "@winonaryder", "WinonaRyderOfficial", "@winonaryder", "Estados Unidos"),
            ("Claire Foy", "https://clairefoy.com", "@clairefoy", "ClaireFoyOfficial", "@clairefoy", "Reino Unido"),
            ("Lee Jung-jae", "https://leejungjae.com", "@from_jjlee", "LeeJungJaeOfficial", "@leejungjae", "Coreia do Sul"),
            ("Andrew Scott", "https://andrewscott.com", "@andrewscott", "AndrewScottOfficial", "@andrewscott", "Reino Unido"),
        ]
        pessoas = {}
        for nome, site, insta, face, twitter, nacionalidade in pessoas_data:
            obj, _ = Pessoa.objects.get_or_create(
                nome=nome,
                defaults={
                    "site": site, "insta": insta, "face": face, "twitter": twitter,
                    "nacionalidade": paises[nacionalidade],
                },
            )
            pessoas[nome] = obj
        self.stdout.write(self.style.SUCCESS(f"Pessoas: {len(pessoas)}"))

        # ---------------------------------------------------------
        # RF01 - Filmes
        # ---------------------------------------------------------
        filmes_data = [
            {
                "nome": "Interestelar",
                "duracao": timedelta(hours=2, minutes=49),
                "sinopse": "Um grupo de exploradores viaja através de um buraco de minhoca em busca de um novo lar para a humanidade.",
                "site_oficial": "https://www.interstellarmovie.net",
                "data_lancamento": date(2014, 11, 6),
                "nota_avaliacao": 9.2,
                "generos": ["Ficção Científica", "Drama"],
                "paises": ["Estados Unidos", "Reino Unido"],
                "diretor": "Christopher Nolan",
            },
            {
                "nome": "A Origem",
                "duracao": timedelta(hours=2, minutes=28),
                "sinopse": "Um ladrão que invade sonhos recebe a missão de plantar uma ideia na mente de um executivo.",
                "site_oficial": "https://www.warnerbros.com/movies/inception",
                "data_lancamento": date(2010, 7, 16),
                "nota_avaliacao": 8.8,
                "generos": ["Ação", "Ficção Científica"],
                "paises": ["Estados Unidos", "Reino Unido"],
                "diretor": "Christopher Nolan",
            },
            {
                "nome": "Ainda Estou Aqui",
                "duracao": timedelta(hours=2, minutes=15),
                "sinopse": "A história de Eunice Paiva, que lutou pela verdade após o desaparecimento do marido durante a ditadura militar.",
                "site_oficial": "https://aindaestouaqui.com.br",
                "data_lancamento": date(2024, 11, 7),
                "nota_avaliacao": 9.0,
                "generos": ["Drama"],
                "paises": ["Brasil"],
                "diretor": "Walter Salles",
            },
            {
                "nome": "Parasita",
                "duracao": timedelta(hours=2, minutes=12),
                "sinopse": "Uma família pobre se infiltra na vida de uma família rica com consequências inesperadas.",
                "site_oficial": "https://www.parasitemovie.net",
                "data_lancamento": date(2019, 5, 30),
                "nota_avaliacao": 8.9,
                "generos": ["Suspense", "Drama", "Comédia"],
                "paises": ["Coreia do Sul"],
                "diretor": "Bong Joon-ho",
            },
            {
                "nome": "Pobres Criaturas",
                "duracao": timedelta(hours=2, minutes=21),
                "sinopse": "Uma jovem é ressuscitada por um cientista excêntrico e embarca em uma jornada de autodescoberta.",
                "site_oficial": "https://www.searchlightpictures.com/poorthings",
                "data_lancamento": date(2023, 12, 8),
                "nota_avaliacao": 8.4,
                "generos": ["Romance", "Ficção Científica", "Comédia"],
                "paises": ["Estados Unidos", "Reino Unido"],
                "diretor": "Yorgos Lanthimos",
            },
        ]
        filmes = {}
        for dados in filmes_data:
            obj, criado = Filme.objects.get_or_create(
                nome=dados["nome"],
                defaults={
                    "duracao": dados["duracao"],
                    "sinopse": dados["sinopse"],
                    "site_oficial": dados["site_oficial"],
                    "data_lancamento": dados["data_lancamento"],
                    "nota_avaliacao": dados["nota_avaliacao"],
                    "diretor": pessoas.get(dados["diretor"]),
                },
            )
            if criado:
                obj.genero.set([generos[g] for g in dados["generos"]])
                obj.pais.set([paises[p] for p in dados["paises"]])
            filmes[dados["nome"]] = obj
        self.stdout.write(self.style.SUCCESS(f"Filmes: {len(filmes)}"))

        # ---------------------------------------------------------
        # RF02 - Filmes com seus Atores
        # ---------------------------------------------------------
        filme_atores_data = [
            ("Interestelar", "Matthew McConaughey", "Cooper"),
            ("A Origem", "Leonardo DiCaprio", "Dom Cobb"),
            ("Ainda Estou Aqui", "Fernanda Torres", "Eunice Paiva"),
            ("Ainda Estou Aqui", "Wagner Moura", "Rubens Paiva"),
            ("Pobres Criaturas", "Emma Stone", "Bella Baxter"),
        ]
        count_fa = 0
        for filme_nome, ator_nome, personagem in filme_atores_data:
            _, criado = FilmeAtor.objects.get_or_create(
                filme=filmes[filme_nome],
                ator=pessoas[ator_nome],
                defaults={"personagem": personagem},
            )
            if criado:
                count_fa += 1
        self.stdout.write(self.style.SUCCESS(f"Relações Filme-Ator: {count_fa}"))

        # ---------------------------------------------------------
        # RF04 - Séries
        # ---------------------------------------------------------
        series_data = [
            {
                "nome": "Stranger Things",
                "duracao": timedelta(minutes=50),
                "sinopse": "Um grupo de amigos enfrenta forças sobrenaturais e experimentos governamentais secretos em Hawkins.",
                "site_oficial": "https://www.netflix.com/title/80057281",
                "data_lancamento": date(2016, 7, 15),
                "nota_avaliacao": 8.7,
                "generos": ["Ficção Científica", "Suspense"],
                "paises": ["Estados Unidos"],
                "diretor": "Matt Duffer",
            },
            {
                "nome": "The Crown",
                "duracao": timedelta(minutes=58),
                "sinopse": "A vida da Rainha Elizabeth II e os eventos que moldaram a segunda metade do século XX.",
                "site_oficial": "https://www.netflix.com/title/80025678",
                "data_lancamento": date(2016, 11, 4),
                "nota_avaliacao": 8.6,
                "generos": ["Drama"],
                "paises": ["Reino Unido"],
                "diretor": "Peter Morgan",
            },
            {
                "nome": "Round 6",
                "duracao": timedelta(minutes=55),
                "sinopse": "Centenas de jogadores endividados aceitam um convite para competir em jogos infantis com apostas mortais.",
                "site_oficial": "https://www.netflix.com/title/81040344",
                "data_lancamento": date(2021, 9, 17),
                "nota_avaliacao": 8.0,
                "generos": ["Suspense", "Drama", "Ação"],
                "paises": ["Coreia do Sul"],
                "diretor": "Hwang Dong-hyuk",
            },
            {
                "nome": "Fleabag",
                "duracao": timedelta(minutes=27),
                "sinopse": "Uma mulher tenta lidar com a vida em Londres enquanto enfrenta luto, relacionamentos e culpa.",
                "site_oficial": "https://www.bbc.co.uk/programmes/p04pmvpj",
                "data_lancamento": date(2016, 7, 21),
                "nota_avaliacao": 8.5,
                "generos": ["Comédia", "Drama"],
                "paises": ["Reino Unido"],
                "diretor": "Phoebe Waller-Bridge",
            },
            {
                "nome": "Round Six: Bastidores",
                "duracao": timedelta(minutes=45),
                "sinopse": "Documentário sobre a produção do fenômeno global de suspense coreano.",
                "site_oficial": "https://www.netflix.com/title/81496742",
                "data_lancamento": date(2022, 1, 1),
                "nota_avaliacao": 7.2,
                "generos": ["Documentário", "Drama"],
                "paises": ["Coreia do Sul"],
                "diretor": "Hwang Dong-hyuk",
            },
        ]
        series = {}
        for dados in series_data:
            obj, criado = Serie.objects.get_or_create(
                nome=dados["nome"],
                defaults={
                    "duracao": dados["duracao"],
                    "sinopse": dados["sinopse"],
                    "site_oficial": dados["site_oficial"],
                    "data_lancamento": dados["data_lancamento"],
                    "nota_avaliacao": dados["nota_avaliacao"],
                    "diretor": pessoas.get(dados["diretor"]),
                },
            )
            if criado:
                obj.genero.set([generos[g] for g in dados["generos"]])
                obj.pais.set([paises[p] for p in dados["paises"]])
            series[dados["nome"]] = obj
        self.stdout.write(self.style.SUCCESS(f"Séries: {len(series)}"))

        # ---------------------------------------------------------
        # RF08 - Temporadas
        # ---------------------------------------------------------
        temporadas_data = [
            ("Stranger Things", 1), ("Stranger Things", 2), ("Stranger Things", 3), ("Stranger Things", 4),
            ("The Crown", 1), ("The Crown", 2), ("The Crown", 3), ("The Crown", 4), ("The Crown", 5), ("The Crown", 6),
            ("Round 6", 1), ("Round 6", 2),
            ("Fleabag", 1), ("Fleabag", 2),
            ("Round Six: Bastidores", 1),
        ]
        temporadas = {}
        for serie_nome, numero in temporadas_data:
            obj, _ = Temporada.objects.get_or_create(
                serie=series[serie_nome], numero=numero
            )
            temporadas[(serie_nome, numero)] = obj
        self.stdout.write(self.style.SUCCESS(f"Temporadas: {len(temporadas)}"))

        # ---------------------------------------------------------
        # RF05 & RF06 - Episódios e Relações Séries-Episódios
        # ---------------------------------------------------------
        episodios_completos = [
            # --- STRANGER THINGS ---
            # T1
            ("Stranger Things", 1, "Capítulo Um: O Desaparecimento de Will Byers", 48, date(2016, 7, 15)),
            ("Stranger Things", 1, "Capítulo Dois: A Esquisita da Rua Maple", 55, date(2016, 7, 15)),
            ("Stranger Things", 1, "Capítulo Três: Luzes de Natal", 51, date(2016, 7, 15)),
            ("Stranger Things", 1, "Capítulo Quatro: O Corpo", 50, date(2016, 7, 15)),
            ("Stranger Things", 1, "Capítulo Cinco: A Pulga e o Acrobata", 53, date(2016, 7, 15)),
            ("Stranger Things", 1, "Capítulo Seis: O Monstro", 47, date(2016, 7, 15)),
            ("Stranger Things", 1, "Capítulo Sete: O Banheiro de Imersão", 42, date(2016, 7, 15)),
            ("Stranger Things", 1, "Capítulo Oito: O Mundo Invertido", 55, date(2016, 7, 15)),
            # T2
            ("Stranger Things", 2, "Capítulo Um: MADMAX", 48, date(2017, 10, 27)),
            ("Stranger Things", 2, "Capítulo Dois: Gostosuras ou Travessuras, Aberração", 56, date(2017, 10, 27)),
            ("Stranger Things", 2, "Capítulo Três: O Girino", 51, date(2017, 10, 27)),
            ("Stranger Things", 2, "Capítulo Quatro: Will, o Sábio", 46, date(2017, 10, 27)),
            ("Stranger Things", 2, "Capítulo Cinco: Dig Dug", 58, date(2017, 10, 27)),
            ("Stranger Things", 2, "Capítulo Seis: O Espião", 51, date(2017, 10, 27)),
            ("Stranger Things", 2, "Capítulo Sete: A Irmã Perdida", 45, date(2017, 10, 27)),
            ("Stranger Things", 2, "Capítulo Oito: O Devorador de Mentes", 47, date(2017, 10, 27)),
            ("Stranger Things", 2, "Capítulo Nove: O Portal", 62, date(2017, 10, 27)),
            # T3
            ("Stranger Things", 3, "Capítulo Um: Suzie, Você Me Ouve?", 50, date(2019, 7, 4)),
            ("Stranger Things", 3, "Capítulo Dois: Os Ratos do Shopping", 50, date(2019, 7, 4)),
            ("Stranger Things", 3, "Capítulo Três: A Salva-Vidas Desaparecida", 50, date(2019, 7, 4)),
            ("Stranger Things", 3, "Capítulo Quatro: O Teste da Sauna", 53, date(2019, 7, 4)),
            ("Stranger Things", 3, "Capítulo Cinco: Os Devorados", 52, date(2019, 7, 4)),
            ("Stranger Things", 3, "Capítulo Seis: E Pluribus Unum", 60, date(2019, 7, 4)),
            ("Stranger Things", 3, "Capítulo Sete: A Mordida", 55, date(2019, 7, 4)),
            ("Stranger Things", 3, "Capítulo Oito: A Batalha de Starcourt", 77, date(2019, 7, 4)),
            # T4
            ("Stranger Things", 4, "Capítulo Um: O Clube do Inferno", 76, date(2022, 5, 27)),
            ("Stranger Things", 4, "Capítulo Dois: A Maldição de Vecna", 77, date(2022, 5, 27)),
            ("Stranger Things", 4, "Capítulo Três: O Monstro e o Super-Herói", 63, date(2022, 5, 27)),
            ("Stranger Things", 4, "Capítulo Quatro: Querido Billy", 77, date(2022, 5, 27)),
            ("Stranger Things", 4, "Capítulo Cinco: Projeto Nina", 75, date(2022, 5, 27)),
            ("Stranger Things", 4, "Capítulo Seis: A Imersão", 73, date(2022, 5, 27)),
            ("Stranger Things", 4, "Capítulo Sete: O Massacre no Laboratório de Hawkins", 98, date(2022, 5, 27)),
            ("Stranger Things", 4, "Capítulo Oito: Papai", 85, date(2022, 7, 1)),
            ("Stranger Things", 4, "Capítulo Nove: O Plano", 150, date(2022, 7, 1)),

            # --- FLEABAG ---
            # T1
            ("Fleabag", 1, "Episódio 1", 27, date(2016, 7, 21)),
            ("Fleabag", 1, "Episódio 2", 25, date(2016, 7, 28)),
            ("Fleabag", 1, "Episódio 3", 26, date(2016, 8, 4)),
            ("Fleabag", 1, "Episódio 4", 25, date(2016, 8, 11)),
            ("Fleabag", 1, "Episódio 5", 24, date(2016, 8, 18)),
            ("Fleabag", 1, "Episódio 6", 26, date(2016, 8, 25)),
            # T2
            ("Fleabag", 2, "Episódio 1", 26, date(2019, 3, 4)),
            ("Fleabag", 2, "Episódio 2", 24, date(2019, 3, 11)),
            ("Fleabag", 2, "Episódio 3", 25, date(2019, 3, 18)),
            ("Fleabag", 2, "Episódio 4", 26, date(2019, 3, 25)),
            ("Fleabag", 2, "Episódio 5", 25, date(2019, 4, 1)),
            ("Fleabag", 2, "Episódio 6", 28, date(2019, 4, 8)),

            # --- ROUND 6 ---
            # T1
            ("Round 6", 1, "Batatinha Frita 1, 2, 3", 60, date(2021, 9, 17)),
            ("Round 6", 1, "Inferno", 63, date(2021, 9, 17)),
            ("Round 6", 1, "O Homem do Guarda-Chuva", 54, date(2021, 9, 17)),
            ("Round 6", 1, "Equipe", 55, date(2021, 9, 17)),
            ("Round 6", 1, "Um Mundo Justo", 52, date(2021, 9, 17)),
            ("Round 6", 1, "Gganbu", 62, date(2021, 9, 17)),
            ("Round 6", 1, "Os VIPs", 58, date(2021, 9, 17)),
            ("Round 6", 1, "O Oitavo Jogador", 32, date(2021, 9, 17)),
            ("Round 6", 1, "Um Dia de Sorte", 55, date(2021, 9, 17)),
            # T2
            ("Round 6", 2, "Pão e Circo", 58, date(2024, 12, 26)),
            ("Round 6", 2, "Mais Uma Rodada", 52, date(2024, 12, 26)),
            ("Round 6", 2, "Regras do Jogo", 56, date(2024, 12, 26)),
            ("Round 6", 2, "Zero Um", 51, date(2024, 12, 26)),
            ("Round 6", 2, "Uma Questão de Sobrevivência", 53, date(2024, 12, 26)),
            ("Round 6", 2, "A Jogada Final", 60, date(2024, 12, 26)),

            # --- THE CROWN ---
            # T1
            ("The Crown", 1, "Wolferton Splash", 57, date(2016, 11, 4)),
            ("The Crown", 1, "Hyde Park Corner", 61, date(2016, 11, 4)),
            ("The Crown", 1, "Windsor", 58, date(2016, 11, 4)),
            ("The Crown", 1, "Ato de Coragem", 58, date(2016, 11, 4)),
            ("The Crown", 1, "Fumaça e Espelhos", 55, date(2016, 11, 4)),
            ("The Crown", 1, "Gelignite", 58, date(2016, 11, 4)),
            ("The Crown", 1, "Conhecimento é Poder", 57, date(2016, 11, 4)),
            ("The Crown", 1, "Orgulho e Alegria", 59, date(2016, 11, 4)),
            ("The Crown", 1, "Assassinos", 56, date(2016, 11, 4)),
            ("The Crown", 1, "Gloriana", 55, date(2016, 11, 4)),
            # T2
            ("The Crown", 2, "Misadventure", 57, date(2017, 12, 8)),
            ("The Crown", 2, "A Company of Men", 54, date(2017, 12, 8)),
            ("The Crown", 2, "Lisbon", 56, date(2017, 12, 8)),
            ("The Crown", 2, "Beryl", 61, date(2017, 12, 8)),
            ("The Crown", 2, "Marionettes", 60, date(2017, 12, 8)),
            # T3
            ("The Crown", 3, "Olding", 54, date(2019, 11, 17)),
            ("The Crown", 3, "Margaretology", 50, date(2019, 11, 17)),
            ("The Crown", 3, "Aberfan", 60, date(2019, 11, 17)),
            ("The Crown", 3, "Bubbikins", 56, date(2019, 11, 17)),
            ("The Crown", 3, "Tywysog Cymru", 54, date(2019, 11, 17)),
            # T4
            ("The Crown", 4, "Gold Stick", 54, date(2020, 11, 15)),
            ("The Crown", 4, "The Balmoral Test", 57, date(2020, 11, 15)),
            ("The Crown", 4, "Fairytale", 54, date(2020, 11, 15)),
            ("The Crown", 4, "Favourites", 57, date(2020, 11, 15)),
            ("The Crown", 4, "48:1", 53, date(2020, 11, 15)),
            # T5
            ("The Crown", 5, "Queen Victoria Syndrome", 53, date(2022, 11, 9)),
            ("The Crown", 5, "The System", 52, date(2022, 11, 9)),
            ("The Crown", 5, "Mou Mou", 51, date(2022, 11, 9)),
            ("The Crown", 5, "Annus Horribilis", 54, date(2022, 11, 9)),
            ("The Crown", 5, "The Way Ahead", 50, date(2022, 11, 9)),
            # T6
            ("The Crown", 6, "Persona Non Grata", 51, date(2023, 11, 16)),
            ("The Crown", 6, "Two Photographs", 48, date(2023, 11, 16)),
            ("The Crown", 6, "Dis-Moi Oui", 55, date(2023, 11, 16)),
            ("The Crown", 6, "Aftermath", 54, date(2023, 11, 16)),
            ("The Crown", 6, "Sleep, Dearie Sleep", 73, date(2023, 12, 14)),

            # --- ROUND SIX: BASTIDORES ---
            ("Round Six: Bastidores", 1, "Especial de Bastidores", 45, date(2022, 1, 1)),
        ]

        count_ep = 0
        count_se = 0

        for serie_nome, temp_num, ep_nome, duracao_min, data_disp in episodios_completos:
            ep_obj, ep_criado = Episodio.objects.get_or_create(nome=ep_nome)
            if ep_criado:
                count_ep += 1

            _, se_criado = SerieEpisodio.objects.get_or_create(
                serie=series[serie_nome],
                temporada=temporadas[(serie_nome, temp_num)],
                episodio=ep_obj,
                defaults={
                    "duracao": timedelta(minutes=duracao_min),
                    "data_disponibilizacao": data_disp,
                },
            )
            if se_criado:
                count_se += 1

        self.stdout.write(self.style.SUCCESS(f"Episódios Cadastrados: {count_ep}"))
        self.stdout.write(self.style.SUCCESS(f"Relações Série-Episódio: {count_se}"))

        self.stdout.write(self.style.SUCCESS("\nBanco de dados populado com sucesso!"))