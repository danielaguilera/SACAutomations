import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from Clases.Destinatario import Destinatario
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from Clases.FileGrouper import DocumentoUnificado

class MailSender:
    def __init__(self, senderUsername: str, senderPassword: str, smtpServer: str, smtpPort: str):
        self.senderUserName: str = senderUsername
        self.senderPassword: str = senderPassword
        self.smtpServer: str = smtpServer
        self.smtpPort: str = smtpPort
        self.session: smtplib.SMTP = None
        
    def startSession(self):
        self.session = smtplib.SMTP(self.smtpServer, self.smtpPort)
        self.session.starttls()
        self.session.login(self.senderUserName, self.senderPassword)
        
    def endSession(self):
        if self.session:
            self.session.quit()
    
    def sendMail(self, receiverAddresss: str, mailSubject: str, mailContent: str, mailAttachment: str):
        self.startSession()
        message = MIMEMultipart()
        message.add_header('from', self.senderUserName)
        message.add_header('to', receiverAddresss)
        message.add_header('subject', mailSubject)
        message.attach(MIMEText(mailContent, 'plain'))
        binaryPDF = open(mailAttachment, 'rb')
        pdfName: str = f'Reportes_semana_{getWeekMondayTimeStamp()}.pdf'
        payload = MIMEBase('application', 'octate-stream', Name=pdfName)
        payload.set_payload((binaryPDF).read())
        encoders.encode_base64(payload)
        payload.add_header('Content-Decomposition', 'attachment', filename=pdfName)
        message.attach(payload)
        self.session.send_message(message)
        self.endSession()
        
    def sendUnifiedDocument(self, destinatario: Destinatario):
        receiverAddress: str = destinatario.correoDestinatario
        receiverAddress: str = 'draguilera@uc.cl' #Hardcoded
        mailSubject: str = f'Envío reportes semana {getWeekMondayTimeStamp()}'
        mailContent: str = f'Estimad@ {destinatario.nombreDestinatario}: \n\n Junto con saludar, se adjunta el resumen de las facturas correspondientes a la semana de {getWeekMondayTimeStamp("long")}'
        mailAttachment: str = f'{DELIVEREDDATAPATH}/{destinatario.nombreDestinatario}/Documento.pdf'
        self.sendMail(receiverAddresss=receiverAddress, mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)
        print(f'Email a {destinatario.correoDestinatario} enviado!')        