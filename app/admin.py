from django.contrib import admin
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


@admin.register(Continente)
class ContinenteAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    search_fields = ("nome",)


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "continente")
    list_filter = ("continente",)
    search_fields = ("nome",)


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    search_fields = ("nome",)


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "nacionalidade", "site", "insta", "face", "twitter")
    list_filter = ("nacionalidade",)
    search_fields = ("nome",)


class FilmeAtorInline(admin.TabularInline):
    model = FilmeAtor
    extra = 1


@admin.register(Filme)
class FilmeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "duracao",
        "data_lancamento",
        "nota_avaliacao",
        "diretor",
    )
    list_filter = ("genero", "pais", "data_lancamento")
    search_fields = ("nome", "sinopse")
    filter_horizontal = ("genero", "pais")
    inlines = [FilmeAtorInline]


@admin.register(FilmeAtor)
class FilmeAtorAdmin(admin.ModelAdmin):
    list_display = ("id", "filme", "ator", "personagem")
    search_fields = ("filme__nome", "ator__nome")


class TemporadaInline(admin.TabularInline):
    model = Temporada
    extra = 1


@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "duracao",
        "data_lancamento",
        "nota_avaliacao",
        "diretor",
    )
    list_filter = ("genero", "pais", "data_lancamento")
    search_fields = ("nome", "sinopse")
    filter_horizontal = ("genero", "pais")
    inlines = [TemporadaInline]


@admin.register(Temporada)
class TemporadaAdmin(admin.ModelAdmin):
    list_display = ("id", "serie", "numero")
    list_filter = ("serie",)


@admin.register(Episodio)
class EpisodioAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    search_fields = ("nome",)


@admin.register(SerieEpisodio)
class SerieEpisodioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "serie",
        "temporada",
        "episodio",
        "duracao",
        "data_disponibilizacao",
    )
    list_filter = ("serie", "temporada")
    search_fields = ("serie__nome", "episodio__nome")