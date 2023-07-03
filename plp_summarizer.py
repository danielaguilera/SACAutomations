import os
import sys
from Utils.Metadata import *
from Clases.SACConnector import SACConnector
from Clases.PLPManager import PLPManager
from datetime import datetime

if __name__ == '__main__':
    plp = PLPManager()
    if len(sys.argv) == 2:
        try:
            date: datetime = datetime.strptime(sys.argv[1], '%d-%m-%Y')
            print('date overwritten')
            plp.fetchDailyMails(date=date)
        except Exception as e:
            print(e)
    else:
        plp.sendSummary()