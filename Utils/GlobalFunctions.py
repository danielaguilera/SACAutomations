from Utils.Metadata import *
from datetime import datetime, timedelta
import locale

def transformDateToSpanish(date : datetime) -> str:
    return f'{WEEKDAYS[date.weekday()]}, {date.day} de {MONTHNAMES[date.month]} de {date.year}'

def transformDateToSpanishBrief(date : datetime) -> str:
    return f'{date.day}-{SHORTMONTHNAMES[date.month]}-{str(date.year)[2::]}'

def getWeekMondayTimeStamp() -> str:
    now: datetime = datetime.now()
    return transformDateToSpanishBrief(now - timedelta(days=now.weekday()))

def setPriceFormat(price: int) -> str:
    locale.setlocale(locale.LC_ALL, '')
    return f'${price:n}'
