from django.contrib import admin
from .models import (
    Continente,
    Pais,
    Genero,
    Pessoa,
    Filme,
    FilmeAtor,
    FilmeImagem,
    Cinema,
    Sessao,
    AvaliacaoUsuario,
    Streaming,
    FilmeStreaming,
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


class FilmeImagemInline(admin.TabularInline):
    model = FilmeImagem
    extra = 1


class SessaoInline(admin.TabularInline):
    model = Sessao
    extra = 1


class FilmeStreamingInline(admin.TabularInline):
    model = FilmeStreaming
    extra = 1


@admin.register(Filme)
class FilmeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "status_cartaz",
        "duracao",
        "data_lancamento",
        "data_estreia_cinema",
        "nota_avaliacao",
        "diretor",
        "trailer_key",
    )
    list_filter = ("status_cartaz", "genero", "pais", "data_lancamento")
    search_fields = ("nome", "sinopse")
    filter_horizontal = ("genero", "pais")
    inlines = [FilmeAtorInline, FilmeImagemInline, SessaoInline, FilmeStreamingInline]


@admin.register(FilmeAtor)
class FilmeAtorAdmin(admin.ModelAdmin):
    list_display = ("id", "filme", "ator", "personagem")
    search_fields = ("filme__nome", "ator__nome")


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "cidade", "estado", "site")
    list_filter = ("cidade", "estado")
    search_fields = ("nome", "cidade")


@admin.register(Sessao)
class SessaoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "filme",
        "cinema",
        "formato",
        "audio",
        "data_inicio_exibicao",
        "data_fim_exibicao",
    )
    list_filter = ("cinema", "formato", "audio")
    search_fields = ("filme__nome", "cinema__nome")


@admin.register(AvaliacaoUsuario)
class AvaliacaoUsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "filme", "usuario", "nota", "data_criacao")
    list_filter = ("nota",)
    search_fields = ("filme__nome", "usuario__username")


@admin.register(Streaming)
class StreamingAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    search_fields = ("nome",)


@admin.register(FilmeStreaming)
class FilmeStreamingAdmin(admin.ModelAdmin):
    list_display = ("id", "filme", "streaming", "tipo")
    list_filter = ("streaming", "tipo")
    search_fields = ("filme__nome",)