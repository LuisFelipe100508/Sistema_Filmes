document.addEventListener('DOMContentLoaded', function () {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function toggleFavorito(filmeId) {
        return fetch('/filme/' + filmeId + '/favoritar/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
            },
        }).then(function (resp) {
            if (resp.status === 403) {
                window.location.href = '/login/';
                return null;
            }
            return resp.json();
        });
    }

    // Botão pequeno (coração nos cartazes de filme)
    document.querySelectorAll('.favorito-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            var filmeId = btn.getAttribute('data-filme-id');

            toggleFavorito(filmeId).then(function (data) {
                if (!data) return;
                if (data.favoritado) {
                    btn.classList.add('ativo');
                } else {
                    btn.classList.remove('ativo');
                    var wrap = btn.closest('.poster-card-wrap');
                    if (wrap && document.getElementById('paginaFavoritos')) {
                        wrap.remove();
                    }
                }
            });
        });
    });

    // Botão grande (página de detalhe do filme)
    var btnGrande = document.getElementById('favoritoDetalheBtn');
    if (btnGrande) {
        btnGrande.addEventListener('click', function (e) {
            e.preventDefault();
            var filmeId = btnGrande.getAttribute('data-filme-id');

            toggleFavorito(filmeId).then(function (data) {
                if (!data) return;
                var span = btnGrande.querySelector('span');
                if (data.favoritado) {
                    btnGrande.classList.add('ativo');
                    if (span) span.textContent = 'Nos favoritos';
                } else {
                    btnGrande.classList.remove('ativo');
                    if (span) span.textContent = 'Adicionar aos favoritos';
                }
            });
        });
    }
});