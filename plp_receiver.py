import imaplib
import email
import sys
import datetime
from datetime import date
from Utils.Metadata import *

imap_server: str = SMTPSERVER
with open(MAILDATA, 'r') as file:
    email_address, password = file.readline().strip().split(',')
email_address = 'draguilera.desarrollos@outlook.com'
password = 'Npphq599123%'

imap = imaplib.IMAP4_SSL(imap_server)
imap.login(email_address, password)

imap.select("Inbox")

today = date.today().strftime('%d-%b-%Y')
_, msgnums = imap.search(None, f'SINCE "{today}"')

for msgnum in msgnums[0].split()[0:1]:
    _, data = imap.fetch(msgnum, '(RFC822)')
    message = email.message_from_bytes(data[0][1])
    print(f"Message Number: {msgnum}")
    print(f"From: {message.get('From')}")
    print(f"To: {message.get('To')}")
    print(f"BCC: {message.get('BCC')}")
    print(f"Date: {message.get('Date')}")
    print(f"Subject: {message.get('Subject')}")

    print(f"Content:")
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            print(part.as_string())
    
    if msgnum == 5:
        break

imap.close()



# mail = imaplib.IMAP4_SSL(SMTPSERVERGYD)

# with open(MAILDATA, 'r') as file:
#     user_name, password = file.readline().strip().split(',')
# mail.login(user_name, password)
# mail.select('INBOX')
# # print(datetime.datetime.today().strftime('%d-%b-%Y'))
# # result, data = mail.search(None, f'''(SINCE "{datetime.datetime.today().strftime('%d-%b-%Y')}")''')
# result, data = mail.search(None, f'''(SINCE 23-May-2023)''')
# email_ids = data[0].split()

# for email_id in email_ids:
#     result, email_data = mail.fetch(email_id, '(RFC822)')
#     raw_email = email_data[0][1]
#     email_message = email.message_from_bytes(raw_email)
#     subject: str = email_message['Subject']
#     sender: str = email_message['From']
#     date = email_message['Date']
#     body = email_message.get_payload()
#     # if 'FINALIZADO' in subject.upper() or 'RETIRO' in subject.upper() or 'TERMINO' in subject.upper() or 'TÉRMINO' in subject.upper() or 'PLP' in subject.upper():
#     #     print(subject)
#     if 'PLP INCUMPLIDO' in subject.upper():
#         print(subject)
#         print(body)
    
#     # print('From:', sender)
#     # print('Date:', date)
#     # print('Body:', body)

# mail.logout()
