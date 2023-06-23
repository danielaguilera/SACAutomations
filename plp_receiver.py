import imaplib
import email
import email.header
import sys
import re
from datetime import date, datetime, timedelta
from unidecode import unidecode
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from Clases.SACConnector import SACConnector
from Clases.Caso import Caso

def extract_rut(text):
    # Find the first rut in the text
    pattern = r"\d{1,3}(?:[.,]?\d{3})*(?:-?\d?k|K)"
    match = re.search(pattern, text)
    
    if match:
        # Extract the found rut and remove the separator characters
        rut = match.group().replace(".", "").replace(",", "").replace("-", "").lower()
        return rut
    
    return None  # If no rut is found
    
def decode_header(text: str) -> str:
    decoded_parts = email.header.decode_header(text)
    decoded_subject = ''
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_subject += part.decode(encoding or 'utf-8')
        else:
            decoded_subject += part
    return decoded_subject

if __name__ == '__main__':
    sacConnector: SACConnector = SACConnector()

    imap_server: str = SMTPSERVERGYD
    with open(MAILDATA, 'r') as file:
        email_address, password = file.readline().strip().split(',')
    # email_address = 'draguilera.desarrollos@outlook.com'
    # password = 'Npphq599123%'

    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(email_address, password)

    imap.select("Inbox")

    today: datetime = datetime.today()
    five_days_ago: datetime = today - timedelta(days=3)
    date_format = "%d-%b-%Y"
    since_date: str = five_days_ago.strftime(date_format)
    until_date: str = today.strftime(date_format)

    _, msgnums = imap.search(None, f'SINCE "{since_date}"')
    # _, msgnums = imap.search(None, f'ALL')

    for msgnum in msgnums[0].split():
        _, data = imap.fetch(msgnum, '(RFC822)')
        message = email.message_from_bytes(data[0][1])
        # print(f"Message Number: {msgnum}")
        # print(f"From: {message.get('From')}")
        # print(f"To: {message.get('To')}")
        # print(f"BCC: {message.get('BCC')}")
        # print(f"Date: {message.get('Date')}")
        # print(f"Subject: {message.get('Subject')}")

        # print(f"Content:")
        # for part in message.walk():
        #     if part.get_content_type() == "text/plain":
        #         print(part.as_string())

        subject: str = decode_header(message.get("Subject")).upper().replace('.', '')
        if any(keyWord in subject for keyWord in SOLICITUD_PLP_KEYWORDS) and PLP in subject:
            print(subject)
            try:
                rutDeudor: str = correctRUTFormat(subject)
                print(f'{subject} => Solicitud de PLP: {rutDeudor}\n')
                casos: list[Caso] = sacConnector.getPossibleMapsaCasos(rutDeudor=rutDeudor)
                if len(casos) == 1:
                    caso: Caso = casos[0]
                    print(f'Caso encontrado: {caso}')
                    if caso.nombreEstado == SUSPENDIDO:
                        with open(PLPREQUESTSPATH, 'a') as file:
                            file.write(f'{datetime.now()}: {caso} ya se encontraba suspendido.')
                        print('El caso ya estaba suspendido')
                    else:
                        sacConnector.setMapsaCasoState(idMapsa=caso.idMapsa, newState=SUSPENDIDO)
                        with open(PLPREQUESTSPATH, 'a') as file:
                            file.write(f'{datetime.now()}: {caso} suspendido exitosamente.')
                        print('Caso suspendido con éxito')
                else:
                    print('No se encontró un caso')
            except Exception:
                print('RUT no encontrado en asunto')
            print('\n\n\n\n')


        elif any(keyWord in subject for keyWord in PLP_INCUMPLIDO_KEYWORDS):
            print(f'{subject} => PLP Incumplido')
            print(f"Content:")
            for n, part in enumerate(message.walk()):
                if part.get_content_type() == "text/plain":
                    print(n)
                    print(part.as_string())
            break
            

    imap.close()

