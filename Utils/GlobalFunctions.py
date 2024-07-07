from Utils.Metadata import *
from datetime import datetime, timedelta, date
import re
import locale
import os
import shutil
import requests

class RunningTask:
    def __init__(self, script: str, user: str):
        self.script = script
        self.user = user

def createCacheFile(user: str, script: str):
    with open(f'{SAC_PATH}/cache_{user}_{script}.txt','w') as file:
        return

def getCacheFiles() -> list[RunningTask]:
    tasks: list[RunningTask] = []
    for filename in os.listdir(SAC_PATH):
        if 'cache' in filename:
            _, user, script = filename.replace('.txt','').split('_')
            task: RunningTask = RunningTask(script=script, user=user)
            tasks.append(task)
    return tasks

def removeCacheFile(user: str, script: str):
    root: str = f'{SAC_PATH}/cache_{user}_{script}.txt'
    if os.path.exists(root):
        os.remove(root)
        
def removeAllCacheFiles():
    for filename in os.listdir(f'{SAC_PATH}'):
        if 'cache' in filename:
            os.remove(f'{SAC_PATH}/{filename}')

def checkInternetConnection():
    try:
        requests.get("http://google.com", timeout=8)
        return True
    except requests.ConnectionError:
        return False

def getCurrentSpanishTimestamp():
    now: datetime = datetime.now()
    return f'{transformDateToSpanish(date=now)} a las {now.strftime("%H:%M:%S")}'

def transformDateToSpanish(date : datetime) -> str:
    return f'{WEEKDAYS[date.weekday()]}, {date.day} de {MONTHNAMES[date.month]} de {date.year}'

def transformDateToSpanishBrief(date : datetime, point: bool = False, english: bool = False) -> str:
    if english:
       return f'{date.day}-{SHORTMONTHNAMESENGLISH[date.month]}-{str(date.year)[2::]}' 
    return f'{date.day}-{SHORTMONTHNAMES[date.month]}{"." if point else ""}-{str(date.year)[2::]}'

def getFormattedMonthFromDate(date: datetime, english: bool = False) -> str:
    if english:
        return f'{SHORTMONTHNAMESENGLISH[date.month]}/{date.year}'
    return f'{SHORTMONTHNAMES[date.month]}./{date.year}'

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
        
def deleteFileIfExists(filename: str) -> None:
    if os.path.exists(filename):
        os.remove(filename)
        
def deleteIfEmpty(path: str) -> None:
    count = 0
    for name in os.listdir(path):
        if name != 'Documento.pdf':
            count += 1
    if not count:
        shutil.rmtree(path=path)
        
def extractNumberFromText(text: str) -> str:
    char: str
    result: str = ''
    for char in text:
        if char.isdigit():
            result += char
    return result

def correctRUTFormat(originalRUT: str) -> str:
    numbers: str = ''
    chr: str
    for chr in originalRUT:
        if chr.isdigit():
            numbers += chr
    if originalRUT[-1].lower() == 'k':
        numbers += 'k'
    if len(numbers) == 8:
        numbers = '0' + numbers
    return numbers[0:2] + '.' + numbers[2:5] + '.' + numbers[5:8] + '-' + numbers[8]

def containsRUT(text: str):
    try:
        return correctRUTFormat(text)
    except Exception:
        return False

def validRUTFormat(originalRUT: str) -> bool:
    return originalRUT == correctRUTFormat(originalRUT=originalRUT)

def validRendicionNumber(rendicionNumber: str) -> bool:
    return rendicionNumber.isdigit()

def validDateFormat(dateString: str) -> bool:
    try:
        datetime.strptime(dateString, '%d-%m-%Y')
        return True
    except ValueError:
        return False        