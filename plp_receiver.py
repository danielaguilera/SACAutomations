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
    
def decode_header(text: str) -> str:
    decoded_parts = email.header.decode_header(text)
    decoded_subject = ''
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_subject += part.decode(encoding or 'utf-8')
        else:
            decoded_subject += part
    return decoded_subject

def cortar_string(string):
    # Buscar la primera aparición de 'OPERACION' en mayúsculas
    inicio = re.search(r'PLP_SECUENCIA', string)
    if not inicio:
        return None

    # Buscar la última aparición de 'PLPN' donde N es un número del 1 al 9
    fin = re.findall(r'PLP[1-9]', string)
    if not fin:
        return None

    # Obtener el índice de la última aparición de 'PLPN'
    ultimo_fin = string.rfind(fin[-1])

    # Cortar el string
    string_cortado = string[inicio.start() + 14:ultimo_fin + 4]

    return string_cortado

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
    five_days_ago: datetime = today - timedelta(days=10)
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
        if False and any(keyWord in subject for keyWord in SOLICITUD_PLP_KEYWORDS) and PLP in subject:
            pass
            try:
                rutDeudor: str = correctRUTFormat(subject)
                print(f'{subject} => Solicitud de PLP: {rutDeudor}\n')
                casos: list[Caso] = sacConnector.getPossibleMapsaCasos(rutDeudor=rutDeudor, active=False)
                if len(casos) == 1:
                    caso: Caso = casos[0]
                    print(f'Caso encontrado: {caso}')
                    if caso.nombreEstado.upper() == SUSPENDIDO:
                        with open(PLPREQUESTSPATH, 'a') as file:
                            file.write(f'{datetime.now()}: {caso} ya se encontraba suspendido.')
                        print('El caso ya estaba suspendido')
                    else:
                        sacConnector.setMapsaCasoState(idMapsa=caso.idMapsa, newState=SUSPENDIDO.lower().capitalize())
                        with open(PLPREQUESTSPATH, 'a') as file:
                            file.write(f'{datetime.now()}: {caso} suspendido exitosamente.')
                        print('Caso suspendido con éxito')
                elif len(casos) > 1:
                    print('Hay más de un caso asociado a este rut')
                else:
                    print('No se encontró un caso')
            except Exception:
                print('RUT no encontrado en asunto')
            print('\n\n\n\n')


        elif any(keyWord in subject for keyWord in PLP_INCUMPLIDO_KEYWORDS):
            print(f'{subject} => PLP Incumplido')
            messageString: str = ''
            for n, part in enumerate(message.walk()):
                if part.get_content_type() == "text/plain":
                    messageString += part.as_string()
            # messageString = messageString[messageString.find('OPERACION')::]
            messageString = cortar_string(messageString)
            tokens: list[str] = list(filter(lambda elem: elem, messageString.split('\n')))
            names: list[str] = []
            for index, element in enumerate(tokens):
                if element.isdigit() and len(element) > 6:
                    names.append(tokens[index + 1])
            for name in names:
                tokenizedName: list[str] = list(filter(lambda word: word and not word.isdigit(), name.split(' ')))
                apellidoDeudor: str = ''
                nombreDeudor: str = ''
                if len(tokenizedName) == 2:
                    apellidoDeudor = tokenizedName[1]
                    nombreDeudor = tokenizedName[0]
                elif len(tokenizedName) >= 3:
                    apellidoDeudor = f'{tokenizedName[-2]} {tokenizedName[-1]}'
                    nombreDeudor = ' '.join(tokenizedName[0:len(tokenizedName)-2])
                print(f'Apellido: {apellidoDeudor} - Nombre: {nombreDeudor}')
                casos: list[Caso] = sacConnector.getPossibleMapsaCasos(apellidoDeudor=apellidoDeudor, nombreDeudor=nombreDeudor, active=False)
                if len(casos) == 1:
                    caso = casos[0]
                    if caso.nombreEstado.upper() == ACTIVO:
                        print(f'Caso {caso.idMapsa} ya estaba activo')
                    else:
                        sacConnector.setMapsaCasoState(idMapsa=caso.idMapsa, newState=ACTIVO.lower().capitalize())
                        print(f'Caso {caso.idMapsa} activado exitosamente')
                else:
                    print('Sin casos')


            
            

    imap.close()

