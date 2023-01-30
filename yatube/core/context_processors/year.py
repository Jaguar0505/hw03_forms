from datetime import date

now = date.today()
now_year = now.year


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': now_year
    }
