import os
from Clases.MailSender import MailSender
from Utils.Metadata import *
from Clases.SACConnector import SACConnector
from Clases.PLPManager import PLPManager
from datetime import datetime
import sys
import io
import traceback

if __name__ == '__main__':
    plp = PLPManager()
    try:
        sinceDate = datetime.strptime(sys.argv[1], '%d-%m-%Y')
    except Exception:
        sinceDate = None
              
    try:
        plp.fetchMailData(date=sinceDate)
    except Exception as e:
        stringBuffer = io.StringIO()
        traceback.print_exc(file=stringBuffer)
        tracebackString = stringBuffer.getvalue()
        stringBuffer.close()
        with open('Params/mail_data.txt') as file:
            username, password = file.readline().strip().split(',')
        server = SMTPSERVERGYD
        port = SMTPPORTGYD
        mailSender: MailSender = MailSender(senderUsername=username, senderPassword=password, smtpServer=server, smtpPort=port)
        mailSender.sendMessage(receiverAddress='draguilera@uc.cl', mailSubject=f'Error - {datetime.now()}', mailContent=tracebackString)
        mailSender.sendMessage(receiverAddress='matias.gause@gmail.com', mailSubject=f'Error - {datetime.now()}', mailContent=tracebackString)
