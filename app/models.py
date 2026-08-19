from django.db import models


# =========================================================
# RF10 - Gerenciar continente
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
# RF09 - Gerenciar países  (nome, [continente])
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
# RF03 - Gerenciar gênero / categoria (nome)
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
# RF07 - Gerenciar atores e diretores
# (nome, site, insta, face, twitter, nacionalidade)
# Usado tanto para Ator quanto para Diretor (mesma estrutura de dados)
# =========================================================
class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
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
# RF01 - Gerenciar filmes
# nome, duracao, sinopse, site_oficial, data_lancamento,
# nota_avaliacao, [genero], [pais], [diretor]
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

    class Meta:
        verbose_name = "Filme"
        verbose_name_plural = "Filmes"
        ordering = ["-data_lancamento"]

    def __str__(self):
        return self.nome


# =========================================================
# RF02 - Gerenciar Filmes com seus atores [filme], [ator]
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
# RF04 - Gerenciar séries (mesma estrutura de Filme)
# =========================================================
class Serie(models.Model):
    nome = models.CharField(max_length=200)
    duracao = models.DurationField(
        help_text="Duração média por episódio - Formato: HH:MM:SS"
    )
    sinopse = models.TextField(blank=True, null=True)
    site_oficial = models.URLField(blank=True, null=True)
    data_lancamento = models.DateField()
    nota_avaliacao = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True
    )

    genero = models.ManyToManyField(Genero, related_name="series", blank=True)
    pais = models.ManyToManyField(Pais, related_name="series", blank=True)
    diretor = models.ForeignKey(
        Pessoa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="series_dirigidas",
    )

    class Meta:
        verbose_name = "Série"
        verbose_name_plural = "Séries"
        ordering = ["-data_lancamento"]

    def __str__(self):
        return self.nome


# =========================================================
# RF08 - Gerenciar temporadas (1º Temporada, 2º Temporada, etc.)
# =========================================================
class Temporada(models.Model):
    serie = models.ForeignKey(
        Serie, on_delete=models.CASCADE, related_name="temporadas"
    )
    numero = models.PositiveIntegerField(help_text="Ex: 1, 2, 3...")

    class Meta:
        verbose_name = "Temporada"
        verbose_name_plural = "Temporadas"
        unique_together = ("serie", "numero")
        ordering = ["serie", "numero"]

    def __str__(self):
        return f"{self.serie.nome} - {self.numero}ª Temporada"


# =========================================================
# RF05 - Gerenciar episódios (nome)
# =========================================================
class Episodio(models.Model):
    nome = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Episódio"
        verbose_name_plural = "Episódios"

    def __str__(self):
        return self.nome


# =========================================================
# RF06 - Gerenciar séries com episódios
# [serie], [temporada], [episodio], duracao, data_disponibilizacao
# =========================================================
class SerieEpisodio(models.Model):
    serie = models.ForeignKey(
        Serie, on_delete=models.CASCADE, related_name="episodios_series"
    )
    temporada = models.ForeignKey(
        Temporada, on_delete=models.CASCADE, related_name="episodios"
    )
    episodio = models.ForeignKey(
        Episodio, on_delete=models.CASCADE, related_name="series_episodios"
    )
    duracao = models.DurationField(help_text="Formato: HH:MM:SS")
    data_disponibilizacao = models.DateField()

    class Meta:
        verbose_name = "Série - Episódio"
        verbose_name_plural = "Séries - Episódios"
        unique_together = ("temporada", "episodio")
        ordering = ["serie", "temporada", "data_disponibilizacao"]

    def __str__(self):
        return f"{self.serie.nome} - {self.temporada} - {self.episodio.nome}"