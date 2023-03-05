import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from Utils.Metadata import *
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
        self.session.login(self.senderUserName, self.senderUserName)
        
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
        with open(mailAttachment, "rb") as f:
            attachment: MIMEApplication = MIMEApplication(f.read(),_subtype="pdf")
        attachment.add_header('Content-Disposition', 'attachment', filename='Reportes')
        message.attach(attachment)
        self.session.send_message(message)
        self.endSession()
        
    def sendUnifiedDocument(self, document: DocumentoUnificado):
        receiverAddress: str = document.destinatario.correoDestinatario
        receiverAddress: str = 'draguilera@uc.cl'
        mailSubject: str = 'Envío reportes'
        mailContent: str = 'Se adjuntan las boletas'
        mailAttachment: str = f'{RESULTPATH}/{document.destinatario.nombreDestinatario}.pdf'
        self.sendMail(receiverAddresss=receiverAddress, mailSubject=mailSubject, mailContent=mailContent, mailAttachment=mailAttachment)        
        


# receivers = ['daniel.aguilera.habbo@gmail.com', 'draguilera@uc.cl']
# mail_subject = 'ejemplo'
# mail_content = 'este es un ejemplo'
# sender_address = 'draguilera@uc.cl'
# sender_pass = 'anything'

# if __name__ == '__main__':
#     #Setup the MIME
#     message = MIMEMultipart()
#     message.add_header('from', sender_address)
#     message.add_header('to', ','.join(receivers))
#     message.add_header('subject', mail_subject) #The subject line
#     #The body and the attachments for the mail
#     message.attach(MIMEText(mail_content, 'plain'))
#     #Create SMTP session for sending the mail

#     filename = f'{RESULTPATH}/Sra. Cecilia Vielma.pdf'
#     # Attach the pdf to the msg going by e-mail
#     with open(filename, "rb") as f:
#         #attach = email.mime.application.MIMEApplication(f.read(),_subtype="pdf")
#         attach = MIMEApplication(f.read(),_subtype="pdf")
#     attach.add_header('Content-Disposition','attachment',filename='Conjunto de reportes')
#     message.attach(attach)
    
#     session = smtplib.SMTP('smtp-mail.outlook.com', 587) #use gmail with port
#     session.starttls() #enable security
#     print(session.login(sender_address, sender_pass)) #login with mail_id and password
#     session.send_message(message)
#     session.quit()
#     print('Mail sent succesfully')
    