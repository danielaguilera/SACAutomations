import imaplib
import email
import sys
import datetime
from Utils.Metadata import *

mail = imaplib.IMAP4_SSL(SMTPSERVERGYD)
with open(MAILDATA, 'r') as file:
    user_name, password = file.readline().strip().split(',')
mail.login(user_name, password)
mail.select('INBOX')
# print(datetime.datetime.today().strftime('%d-%b-%Y'))
# result, data = mail.search(None, f'''(SINCE "{datetime.datetime.today().strftime('%d-%b-%Y')}")''')
result, data = mail.search(None, f'''(SINCE 25-May-2023)''')
email_ids = data[0].split()

for email_id in email_ids:
    result, email_data = mail.fetch(email_id, '(RFC822)')
    raw_email = email_data[0][1]
    email_message = email.message_from_bytes(raw_email)
    subject: str = email_message['Subject']
    sender: str = email_message['From']
    date = email_message['Date']
    body = email_message.get_payload(decode=True)
    # if 'FINALIZADO' in subject.upper() or 'RETIRO' in subject.upper() or 'TERMINO' in subject.upper() or 'TÉRMINO' in subject.upper() or 'PLP' in subject.upper():
    #     print(subject)
    if 'PLP INCUMPLIDO' in subject.upper():
        print(body)
    
    # print('From:', sender)
    # print('Date:', date)
    # print('Body:', body)

mail.logout()
