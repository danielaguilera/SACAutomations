import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

sender_email = 'daniel.aguilera.habbo@gmail.com'
recipient_email = 'draguilera@uc.cl'

# Set up the email message
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = recipient_email
message['Subject'] = 'ATTACHMENT TEST'

# Attach the PDF file
with open('Resultados/Sra. Cecilia Vielma.pdf', 'rb') as file:
    attachment = MIMEApplication(file.read(), _subtype='pdf')
    attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename('Resultados/Sra. Cecilia Vielma.pdf'))
    message.attach(attachment)

# Send the email using SMTP
smtp_server = 'smtp-mail.outlook.com'
smtp_port = 587
smtp_username = 'draguilera@uc.cl'
smtp_password = 'Npphq599123%'

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(sender_email, recipient_email, message.as_string())
    server.quit()

print('Email sent successfully!')
    
    