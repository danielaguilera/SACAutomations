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
        # self.session = smtplib.SMTP(self.smtpServer, self.smtpPort)
        # self.session.starttls()
        # self.session.login(self.senderUserName, self.senderPassword)
        # message = MIMEMultipart()
        # message.add_header('from', self.senderUserName)
        # message.add_header('to', receiverAddresss)
        # message.add_header('subject', mailSubject)
        # message.attach(MIMEText(mailContent, 'plain'))
        # binaryPDF = open(mailAttachment, 'rb')
        # pdfName: str = f'Reportes_semana_{getWeekMondayTimeStamp()}.pdf'
        # payload = MIMEBase('application', 'octate-stream', Name=pdfName)
        # payload.set_payload((binaryPDF).read())
        # encoders.encode_base64(payload)
        # payload.add_header('Content-Decomposition', 'attachment', filename=pdfName)
        # message.attach(payload)
        # self.session.send_message(message)
        # self.session.quit()
        
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
