
from datetime import date

def get_period_dates(period, year):
    period_mapping = {
        "январь": (date(year, 1, 1), date(year, 1, 31)),
        "февраль": (date(year, 2, 1), date(year, 2, 28)),
        "март": (date(year, 3, 1), date(year, 3, 31)),
        "апрель": (date(year, 4, 1), date(year, 4, 30)),
        "май": (date(year, 5, 1), date(year, 5, 31)),
        "июнь": (date(year, 6, 1), date(year, 6, 30)),
        "июль": (date(year, 7, 1), date(year, 7, 31)),
        "август": (date(year, 8, 1), date(year, 8, 31)),
        "сентябрь": (date(year, 9, 1), date(year, 9, 30)),
        "октябрь": (date(year, 10, 1), date(year, 10, 31)),
        "ноябрь": (date(year, 11, 1), date(year, 11, 30)),
        "декабрь": (date(year, 12, 1), date(year, 12, 31)),
        "1-й квартал": (date(year, 1, 1), date(year, 3, 31)),
        "2-й квартал": (date(year, 4, 1), date(year, 6, 30)),
        "3-й квартал": (date(year, 7, 1), date(year, 9, 30)),
        "4-й квартал": (date(year, 10, 1), date(year, 12, 31)),
        "1-е полугодие": (date(year, 1, 1), date(year, 6, 30)),
        "2-е полугодие": (date(year, 7, 1), date(year, 12, 31)),
        "год": (date(year, 1, 1), date(year, 12, 31))
    }

    return period_mapping.get(period, (None, None))