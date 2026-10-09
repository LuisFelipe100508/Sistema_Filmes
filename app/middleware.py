from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse


class LoginOuVisitanteMiddleware:
    """
    Porta de entrada do site: quem não está logado e não escolheu
    "Entrar como visitante" é enviado para a tela de login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._acesso_liberado(request):
            return self.get_response(request)
        return redirect_to_login(request.get_full_path(), reverse("app:login"))

    def _acesso_liberado(self, request):
        if request.user.is_authenticated or request.session.get("visitante"):
            return True

        livres = (
            reverse("app:login"),
            reverse("app:registrar"),
            reverse("app:entrar_visitante"),
            "/admin/",
            settings.STATIC_URL,
        )
        return request.path.startswith(livres)