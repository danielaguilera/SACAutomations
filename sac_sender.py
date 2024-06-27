from Clases.SACSenderJob import SACSenderJob
from Clases.MailSender import MailSender
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from tkinter import messagebox
import logging
import io
import traceback

if __name__ == '__main__':
    if getCacheFiles():
        print('Aplicación en uso')
    else:
        with open('Params/mail_data.txt') as file:
            username, password = file.readline().strip().split(',')
        server = SMTPSERVERGYD
        port = SMTPPORTGYD
        try:
            createCacheFile(user='SERVIDOR', script=SENDING_ACTIVITY)
            sacSenderjob: SACSenderJob = SACSenderJob()
            sacSenderjob.generateUnifiedDocument()
            sacSenderjob.sendReports()
            removeCacheFile(user='SERVIDOR', script=SENDING_ACTIVITY)
        except Exception as e:
            stringBuffer = io.StringIO()
            traceback.print_exc(file=stringBuffer)
            tracebackString = stringBuffer.getvalue()
            stringBuffer.close()
            with open('SAC_SENDER_ERROR.txt','w') as file:
                file.write(tracebackString)
            mailSender: MailSender = MailSender(senderUsername=username, senderPassword=password, smtpServer=server, smtpPort=port)
            mailSender.sendMessage(receiverAddress='draguilera@uc.cl', mailSubject=f'[SAC SENDER] - [Error] - {datetime.now()}', mailContent=tracebackString)
        finally:
            removeCacheFile(user='SERVIDOR', script=SENDING_ACTIVITY)
    
    
        



