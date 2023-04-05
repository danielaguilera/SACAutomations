from Utils.Metadata import *
from datetime import datetime, timedelta, date
import locale
import os
import shutil

def transformDateToSpanish(date : datetime) -> str:
    return f'{WEEKDAYS[date.weekday()]}, {date.day} de {MONTHNAMES[date.month]} de {date.year}'

def transformDateToSpanishBrief(date : datetime) -> str:
    return f'{date.day}-{SHORTMONTHNAMES[date.month]}-{str(date.year)[2::]}'

def getWeekMondayTimeStamp(format: str = 'short') -> str:
    now: datetime = datetime.now()
    timeDelta: timedelta = now - timedelta(days=now.weekday())
    return transformDateToSpanishBrief(timeDelta) if format == 'short' else transformDateToSpanish(timeDelta)

def getDateFromSpanishFormat(stringDate: str) -> datetime:
    stringDate = stringDate.replace('del', 'de').lower()
    dayString, monthString, yearString = stringDate.split('de')
    day: int = int(dayString)
    month: int = 0
    for monthNumber in MONTHNAMES:
        if MONTHNAMES[monthNumber] == monthString.strip():
            month = monthNumber
            break
    year: int = int(yearString)
    return date(year=year, month=month, day=day)

def setPriceFormat(price: int) -> str:
    locale.setlocale(locale.LC_ALL, '')
    return f'${price:n}'

def deleteIfExists(path: str) -> None:
    if os.path.exists(path):
        shutil.rmtree(path=path)
        
def extractNumberFromText(text: str) -> str:
    char: str
    result: str = ''
    for char in text:
        if char.isdigit():
            result += char
    return result

