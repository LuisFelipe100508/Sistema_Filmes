from django.db import models
from django.contrib.auth.models import User


# =========================================================
# Continente
# =========================================================
class Continente(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Continente"
        verbose_name_plural = "Continentes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =========================================================
# País
# =========================================================
class Pais(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    continente = models.ForeignKey(
        Continente, on_delete=models.CASCADE, related_name="paises"
    )

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =========================================================
# Gênero / categoria
# =========================================================
class Genero(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Gênero"
        verbose_name_plural = "Gêneros"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =========================================================
# Pessoa (atores e diretores)
# =========================================================
class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
    foto_url = models.URLField(blank=True, null=True, help_text="Foto do ator/diretor (TMDB)")
    site = models.URLField(blank=True, null=True)
    insta = models.CharField("Instagram", max_length=150, blank=True, null=True)
    face = models.CharField("Facebook", max_length=150, blank=True, null=True)
    twitter = models.CharField("Twitter", max_length=150, blank=True, null=True)
    nacionalidade = models.ForeignKey(
        Pais, on_delete=models.SET_NULL, null=True, blank=True, related_name="pessoas"
    )

    class Meta:
        verbose_name = "Pessoa (Ator/Diretor)"
        verbose_name_plural = "Pessoas (Atores/Diretores)"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =========================================================
# Filme
# =========================================================
class Filme(models.Model):
    nome = models.CharField(max_length=200)
    duracao = models.DurationField(help_text="Formato: HH:MM:SS")
    sinopse = models.TextField(blank=True, null=True)
    site_oficial = models.URLField(blank=True, null=True)
    data_lancamento = models.DateField()
    nota_avaliacao = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True
    )

    genero = models.ManyToManyField(Genero, related_name="filmes", blank=True)
    pais = models.ManyToManyField(Pais, related_name="filmes", blank=True)
    diretor = models.ForeignKey(
        Pessoa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="filmes_dirigidos",
    )

    # Integração com TMDB (The Movie Database)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True, help_text="ID do filme na API do TMDB")
    poster_url = models.URLField(blank=True, null=True, help_text="URL da capa/poster do filme")
    backdrop_url = models.URLField(blank=True, null=True, help_text="URL da imagem de fundo (banner)")
    trailer_key = models.CharField(max_length=30, blank=True, null=True, help_text="ID do vídeo no YouTube (trailer)")

    # Status em relação aos cinemas/catálogo
    STATUS_CHOICES = [
        ("em_cartaz", "Em cartaz"),
        ("em_breve", "Em breve"),
        ("lancado", "Já lançado"),
    ]
    status_cartaz = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="lancado",
        help_text="Situação do filme no catálogo"
    )
    data_estreia_cinema = models.DateField(
        null=True, blank=True,
        help_text="Data de estreia nos cinemas (pode ser diferente de data_lancamento)"
    )

    class Meta:
        verbose_name = "Filme"
        verbose_name_plural = "Filmes"
        ordering = ["-data_lancamento"]

    def __str__(self):
        return self.nome


# =========================================================
# Filme - Ator (elenco)
# =========================================================
class FilmeAtor(models.Model):
    filme = models.ForeignKey(Filme, on_delete=models.CASCADE, related_name="elenco")
    ator = models.ForeignKey(
        Pessoa, on_delete=models.CASCADE, related_name="filmes_atuados"
    )
    personagem = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = "Filme - Ator"
        verbose_name_plural = "Filmes - Atores"
        unique_together = ("filme", "ator")

    def __str__(self):
        return f"{self.ator} em {self.filme}"


# =========================================================
# Galeria de imagens extras do filme (pra slideshow de fundo)
# =========================================================
class FilmeImagem(models.Model):
    filme = models.ForeignKey(Filme, on_delete=models.CASCADE, related_name="galeria")
    url = models.URLField()
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Imagem do Filme"
        verbose_name_plural = "Galeria de Imagens"
        ordering = ["ordem"]

    def __str__(self):
        return f"Imagem {self.ordem} de {self.filme.nome}"


# =========================================================
# Cinema - representa uma sala/rede de cinema da região
# =========================================================
class Cinema(models.Model):
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, help_text="Sigla, ex: MG")
    site = models.URLField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        verbose_name = "Cinema"
        verbose_name_plural = "Cinemas"
        ordering = ["cidade", "nome"]

    def __str__(self):
        return f"{self.nome} ({self.cidade}/{self.estado})"


# =========================================================
# Sessao - liga um Filme a um Cinema, com o período de exibição
# =========================================================
class Sessao(models.Model):
    filme = models.ForeignKey(Filme, on_delete=models.CASCADE, related_name="sessoes")
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="sessoes")

    data_inicio_exibicao = models.DateField(help_text="Desde quando está passando neste cinema")
    data_fim_exibicao = models.DateField(
        null=True, blank=True,
        help_text="Até quando fica em cartaz neste cinema (em branco = indefinido)"
    )

    FORMATO_CHOICES = [
        ("2D", "2D"),
        ("3D", "3D"),
        ("IMAX", "IMAX"),
        ("4DX", "4DX"),
    ]
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default="2D")

    LEGENDA_CHOICES = [
        ("dublado", "Dublado"),
        ("legendado", "Legendado"),
        ("original", "Idioma original"),
    ]
    audio = models.CharField(max_length=10, choices=LEGENDA_CHOICES, default="dublado")

    horarios = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Horários das sessões, separados por vírgula. Ex: 14:00, 17:30, 20:45"
    )

    class Meta:
        verbose_name = "Sessão"
        verbose_name_plural = "Sessões"
        ordering = ["-data_inicio_exibicao"]
        unique_together = ("filme", "cinema", "formato", "audio")

    def __str__(self):
        return f"{self.filme.nome} em {self.cinema.nome} ({self.formato}/{self.audio})"

    @property
    def em_cartaz_agora(self):
        from datetime import date
        hoje = date.today()
        if self.data_inicio_exibicao > hoje:
            return False
        if self.data_fim_exibicao and self.data_fim_exibicao < hoje:
            return False
        return True


# =========================================================
# Avaliação de usuários — comentários sobre filmes já assistidos
# =========================================================
class AvaliacaoUsuario(models.Model):
    filme = models.ForeignKey(Filme, on_delete=models.CASCADE, related_name="avaliacoes_usuarios")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avaliacoes")
    nota = models.PositiveSmallIntegerField(help_text="Nota de 1 a 5 estrelas")
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avaliação de Usuário"
        verbose_name_plural = "Avaliações de Usuários"
        ordering = ["-data_criacao"]
        unique_together = ("filme", "usuario")

    def __str__(self):
        return f"{self.usuario.username} avaliou {self.filme.nome} ({self.nota}★)"


# =========================================================
# Onde assistir em streaming (Netflix, Prime Video, etc.)
# =========================================================
class Streaming(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    logo_url = models.URLField(blank=True, null=True)
    tmdb_provider_id = models.IntegerField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Serviço de Streaming"
        verbose_name_plural = "Serviços de Streaming"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class FilmeStreaming(models.Model):
    TIPO_CHOICES = [
        ("assinatura", "Incluído na assinatura"),
        ("aluguel", "Aluguel"),
        ("compra", "Compra"),
    ]
    filme = models.ForeignKey(Filme, on_delete=models.CASCADE, related_name="streamings")
    streaming = models.ForeignKey(Streaming, on_delete=models.CASCADE, related_name="filmes")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="assinatura")

    class Meta:
        verbose_name = "Filme no Streaming"
        verbose_name_plural = "Filmes no Streaming"
        unique_together = ("filme", "streaming", "tipo")

    def __str__(self):
        return f"{self.filme.nome} em {self.streaming.nome} ({self.get_tipo_display()})"