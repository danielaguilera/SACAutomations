import os
from Clases.MailSender import MailSender
from Utils.Metadata import *
from Clases.SACConnector import SACConnector
from Clases.PLPManager import PLPManager
from datetime import datetime

if __name__ == '__main__':
    plp = PLPManager()
    try:
        plp.fetchMailData()
    except Exception as e:
        with open('Params/mail_data.txt') as file:
            username, password = file.readline().strip().split(',')
        server = SMTPSERVERGYD
        port = SMTPPORTGYD
        mailSender: MailSender = MailSender(senderUsername=username, senderPassword=password, smtpServer=server, smtpPort=port)
        mailSender.sendMessage(receiverAddress='draguilera@uc.cl', mailSubject=f'Error - {datetime.now()}', mailContent=str(e))
