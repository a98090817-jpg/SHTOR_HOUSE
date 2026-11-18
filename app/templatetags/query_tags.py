"""Katalog havolalari uchun yordamchi template teglari."""

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def query_url(context, **kwargs):
    """Joriy GET parametrlarini saqlab, keraklilarini o'zgartiradi.

    `None` berilgan parametr URL dan olib tashlanadi. Natija bo'sh bo'lsa,
    ortiqcha `?` belgisi qo'shilmaydi (Django'ning `{% querystring %}` tegi
    bo'sh holatda ham `?` qaytaradi).
    """
    request = context.get('request')
    params = request.GET.copy() if request is not None else {}
    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value
    encoded = params.urlencode()
    return f'?{encoded}' if encoded else ''
