from Clases.SACSenderJob import SACSenderJob
from Utils.Metadata import *
from tkinter import messagebox
import logging

if __name__ == '__main__':
    sacSenderjob: SACSenderJob = SACSenderJob()
    sacSenderjob.generateUnifiedDocument()
    sacSenderjob.sendReports()

    
    
    
        



