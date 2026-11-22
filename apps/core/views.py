
from django.shortcuts import render


def home(request):
    """Отображает главную страницу базы знаний ITALIA ARCHIVE."""
    return render(request, 'core/home.html')
