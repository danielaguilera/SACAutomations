from email.mime.application import MIMEApplication
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from Clases.Destinatario import Destinatario
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from Clases.FileGrouper import DocumentoUnificado
from Clases.SACConnector import SACConnector

class MailSender:
    def __init__(self, senderUsername: str, senderPassword: str, smtpServer: str, smtpPort: str):
        self.senderUserName: str = senderUsername
        self.senderPassword: str = senderPassword
        self.smtpServer: str = smtpServer
        self.smtpPort: str = smtpPort
        self.session: smtplib.SMTP = None
        self.sacConnector: SACConnector = SACConnector()
    
    def sendMail(self, receiverAddress: str, mailSubject: str, mailContent: str, mailAttachment: str):
        msg = MIMEMultipart()
        msg['From'] = self.senderUserName
        msg['To'] = receiverAddress
        msg['Subject'] = mailSubject
        msg.attach(MIMEText(mailContent, 'plain'))
        with open(mailAttachment, "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="pdf")
            attach.add_header('Content-Disposition','attachment',filename='Resumen.pdf')
            msg.attach(attach)
        server = smtplib.SMTP_SSL(self.smtpServer, self.smtpPort)
        server.login(self.senderUserName, self.senderPassword)
        server.sendmail(self.senderUserName, receiverAddress, msg.as_string())
        server.quit()

    def sendPLPMail(self, receiverAddress: str, mailSubject: str, mailContent: str, mailAttachment: str):
        msg = MIMEMultipart()
        msg['From'] = self.senderUserName
        msg['To'] = receiverAddress
        msg['Subject'] = mailSubject
        msg.attach(MIMEText(mailContent, 'plain'))
        with open(mailAttachment, "rb") as f:
            attach = MIMEApplication(f.read(),_subtype="xlsx")
            attach.add_header('Content-Disposition','attachment',filename='Resumen.xlsx')
            msg.attach(attach)
        server = smtplib.SMTP_SSL(self.smtpServer, self.smtpPort)
        server.login(self.senderUserName, self.senderPassword)
        server.sendmail(self.senderUserName, receiverAddress, msg.as_string())
        server.quit()

        
    def sendUnifiedDocument(self, destinatario: Destinatario):
        receiverAddress: str = destinatario.correoDestinatario
        mailSubject: str = f'{"DEMO - ESTE EMAIL ES UNA PRUEBA Y NO CUENTA - " if SEND != "send" else ""}Envío reportes semana {getWeekMondayTimeStamp()}'
        mailContent: str = f'Estimad@ {destinatario.nombreDestinatario}: \n\n Junto con saludar, se adjunta el resumen de las facturas correspondientes a la semana de {getWeekMondayTimeStamp("long")}'
        mailAttachment: str = f'{DELIVEREDDATAPATH}/{destinatario.nombreDestinatario}/Documento.pdf'
        if SEND == 'send':
            self.sendMail(receiverAddress=receiverAddress, mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
            ccs: list[str] = self.sacConnector.getCCByDestinatario(nombreDestinatario=destinatario.nombreDestinatario)
            for cc in ccs:
                self.sendMail(receiverAddress=cc, mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        self.sendMail(receiverAddress='daniel.aguilera.habbo@gmail.com', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        self.sendMail(receiverAddress='draguilera@uc.cl', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        self.sendMail(receiverAddress='servidor@gydabogados.cl', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        self.sendMail(receiverAddress='matias.gause@gmail.com', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        self.sendMail(receiverAddress='vahumada@gydabogados.cl', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        with open(ACTIVITYLOGFILE, 'a') as file:
            file.write(f'{str(datetime.now())}: {USER} envió los resúmenes de la semana {getWeekMondayTimeStamp()} a {destinatario.correoDestinatario} ({"OFICIAL" if SEND == "send" else "DEMO"})\n')
        print(f'Email a {destinatario.correoDestinatario} enviado!')

    def sendPLPSummary(self):
        mailSubject: str = f'Resumen Solicitudes PLP y PLP incumplido'
        mailContent: str = f'Se adjuntan las solictudes al dá de hoy {transformDateToSpanish(date=datetime.now())}'
        mailAttachment: str = f'{PLPREQUESTSPATH}'
        self.sendPLPMail(receiverAddress='daniel.aguilera.habbo@gmail.com', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        self.sendPLPMail(receiverAddress='draguilera@uc.cl', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        # self.sendPLPMail(receiverAddress='servidor@gydabogados.cl', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        # self.sendPLPMail(receiverAddress='matias.gause@gmail.com', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        # self.sendPLPMail(receiverAddress='vahumada@gydabogados.cl', mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)      
