
from django.shortcuts import render, get_object_or_404

from .models import City, Style, Epoch, Architect


def references_home(request):
    """Отображает главную страницу справочников."""

    return render(request, 'references/references_home.html')


def cities_list(request):
    """Отображает список городов."""

    cities = City.objects.all().order_by('name')

    return render(
        request,
        'references/cities_list.html',
        {'cities': cities}
    )


def styles_list(request):
    """Отображает список архитектурных стилей."""

    styles = Style.objects.select_related(
        'parent_style'
    ).all().order_by('name')

    return render(
        request,
        'references/styles_list.html',
        {'styles': styles}
    )


def epochs_list(request):
    """Отображает список исторических эпох."""

    epochs = Epoch.objects.all().order_by('year_start', 'name')

    return render(
        request,
        'references/epochs_list.html',
        {'epochs': epochs}
    )


def architects_list(request):
    """Отображает список архитекторов."""

    architects = Architect.objects.all().order_by('full_name')

    return render(
        request,
        'references/architects_list.html',
        {'architects': architects}
    )
