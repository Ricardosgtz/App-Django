from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

# 🌍 Vista raíz para evitar "página no responde"
def home(request):
    return JsonResponse({
        "message": "✅ Servidor Django funcionando correctamente.",
        "status": "OK",
        "author": "Ricardo Santos",
    })

urlpatterns = [
    path('', home),  # 🔹 Respuesta para la raíz del dominio

    path('admin/', admin.site.urls),

    # ✅ Rutas de tus aplicaciones (sin slash inicial, con slash final)
    path('clients', include('clients.urls')),
    path('auth', include('authentication.urls')),
    path('categories', include('categories.urls')),
    path('products', include('products.urls')),
    path('address', include('address.urls')),
    path('orders', include('orders.urls')),
]

# ⚙️ Sirve archivos estáticos y media en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # 🧩 Necesario para servir imágenes en producción (Render)
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
