from Metadata import *
from datetime import datetime

def transformDateToSpanish(date : datetime) -> str:
    return f'{WEEKDAYS[date.weekday()]}, {date.day} de {MONTHNAMES[date.month]} de {date.year}'

def transformDateToSpanishBrief(date : datetime) -> str:
    return f'{date.day}-{SHORTMONTHNAMES[date.month]}-{str(date.year)[2::]}'