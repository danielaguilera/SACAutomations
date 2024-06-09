from Clases.SACSenderJob import SACSenderJob
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from tkinter import messagebox
import logging

if __name__ == '__main__':
    if getCacheFiles():
        print('Aplicación en uso')
    else:
        createCacheFile(user='SERVIDOR', script=SENDING_ACTIVITY)
        sacSenderjob: SACSenderJob = SACSenderJob()
        sacSenderjob.generateUnifiedDocument()
        sacSenderjob.sendReports()
        removeCacheFile(user='SERVIDOR', script=SENDING_ACTIVITY)

    
    
    
        



