from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render

def root_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_librarian_or_admin:
            return redirect('dashboard:admin_dashboard')
        return redirect('dashboard:member_dashboard')
    return render(request, 'landing.html')

urlpatterns = [
    path('', root_redirect, name='root_landing'),
    path('django-admin/', admin.site.urls),
    path('accounts/', include('library.accounts.urls', namespace='accounts')),
    path('dashboard/', include('library.dashboard.urls', namespace='dashboard')),
    path('authors/', include('library.authors.urls', namespace='authors')),
    path('books/', include('library.books.urls', namespace='books')),
    path('circulation/', include('library.circulation.urls', namespace='circulation')),
]

# Serve media and static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
