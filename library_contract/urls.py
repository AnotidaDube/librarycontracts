from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from contracts import views as contract_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contracts/', include('contracts.urls')),
    path('', contract_views.welcome, name='home'),
]

# This allows you to open the PDF files in your browser while testing
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)