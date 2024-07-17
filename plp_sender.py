import os
import sys
from Clases.SACConnector import SACConnector
from Clases.PLPManager import PLPManager
from datetime import datetime

if __name__ == '__main__':
    plp = PLPManager()
    try:
        date: datetime = datetime.strptime(input("Fecha: "), '%d-%m-%Y')
        plp.fetchDailyMails(date=date)
    except Exception:
        print('Formato incorrecto')