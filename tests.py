import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from Utils.Metadata import *

class Sender:
    def __init__(self, senderUsername: str, senderPassword: str, smtpServer: str, smtpPort: str):
        self.senderUserName: str = senderUsername
        self.senderPassword: str = senderPassword
        self.smtpServer: str = smtpServer
        self.smtpPort: str = smtpPort
        self.receivers: list[str] = []

receivers = ['daniel.aguilera.habbo@gmail.com', 'draguilera@uc.cl']
mail_subject = 'ejemplo'
mail_content = 'este es un ejemplo'
sender_address = 'draguilera@uc.cl'
sender_pass = 'Npphq599123%'

if __name__ == '__main__':
    #Setup the MIME
    message = MIMEMultipart()
    message.add_header('from', sender_address)
    message.add_header('to', ','.join(receivers))
    message.add_header('subject', mail_subject) #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail

    filename = f'{RESULTPATH}/Sra. Cecilia Vielma.pdf'
    # Attach the pdf to the msg going by e-mail
    with open(filename, "rb") as f:
        #attach = email.mime.application.MIMEApplication(f.read(),_subtype="pdf")
        attach = MIMEApplication(f.read(),_subtype="pdf")
    attach.add_header('Content-Disposition','attachment',filename='Conjunto de reportes')
    message.attach(attach)
    
    session = smtplib.SMTP('smtp-mail.outlook.com', 587) #use gmail with port
    session.starttls() #enable security
    print(session.login(sender_address, sender_pass)) #login with mail_id and password
    session.send_message(message)
    session.quit()
    print('Mail sent succesfully')
    