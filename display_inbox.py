import sys
from Utils.Metadata import *
from Clases.PLPManager import PLPManager
import imaplib
import email
import email.header
from email.message import Message
from datetime import datetime, timedelta

def decodeHeader(text: str) -> str:
    try:
        decodedParts = email.header.decode_header(text)
        decodedSubject = ''
        for part, encoding in decodedParts:
            if isinstance(part, bytes):
                decodedSubject += part.decode(encoding or 'utf-8')
            else:
                decodedSubject += part
        return decodedSubject
    except Exception:
        return ''

if __name__ == "__main__":
    
    try:
        startDate = datetime.strptime(sys.argv[1], '%d-%m-%Y')
        endDate = datetime.strptime(sys.argv[2], '%d-%m-%Y')
    except Exception:
        print('Formato inválido')
        sys.exit()
    
    imap = imaplib.IMAP4_SSL(SMTPSERVERGYD)
    with open(MAILDATA, 'r') as file:
        username, password = file.readline().strip().split(',')
    imap.login(username, password)
    imap.select("Inbox")
    sinceDate: str = startDate.strftime('%d-%b-%Y')
    beforeDate: str = endDate.strftime('%d-%b-%Y')
    _, msgnums = imap.search(None, f'(SINCE {sinceDate} BEFORE {beforeDate})')
    msgIds = msgnums[0].split()
    for msgnum in msgIds:
        _, data = imap.fetch(msgnum, '(RFC822)')
        message: Message = email.message_from_bytes(data[0][1])
        messageSender: str = decodeHeader(message.get('From'))
        messageDate: str = message.get('Date')
        messageSubject: str = decodeHeader(message.get('Subject'))
        messageString: str = ''
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                messageString += part.as_string()
        print(messageSubject)
                 