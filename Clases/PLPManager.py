from Clases.SACConnector import SACConnector
from Clases.MailSender import MailSender
import imaplib
import email
import email.header
from email.message import Message
import sys
import re
from datetime import date, datetime, timedelta, time
from unidecode import unidecode
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from Clases.Caso import Caso
from Clases.Deudor import Deudor
import pytz
import openpyxl

class GYDEmail:
    def __init__(self, sender: str, subject: str, date: str):
        self.sender: str = sender
        self.subject: str = subject
        self.date: str = date

class PLPRequest:
    def __init__(self, payload: GYDEmail, rutDeudor: str = '', caso: Caso = None):
        self.rutDeudor: str = rutDeudor
        self.caso: Caso = caso
        self.payload: GYDEmail = payload

    def __str__(self):
        return f'Solicitud PLP: {self.rutDeudor}'
    
    def __repr__(self):
        return self.__str__()

class PLPBreached:
    def __init__(self, payload: GYDEmail, deudores: list[Deudor] = []):
        self.deudores: list[Deudor] = deudores
        self.payload: GYDEmail = payload

    def __str__(self):
        return f'PLP Incumplido: {",".join([deudor.rawName for deudor in self.deudores])}'

    def __repr__(self):
        return self.__str__()

class SACRequests:
    def __init__(self, plpRequests: list[PLPRequest], plpBreachedRequests: list[PLPBreached]):
        self.plpRequests = plpRequests
        self.plpBreachedRequests = plpBreachedRequests

    def __str__(self):
        return '\n'.join([str(elem) for elem in self.plpRequests + self.plpBreachedRequests])

class PLPManager:
    def __init__(self):
        self.sacConnector: SACConnector = SACConnector()
        self.smtpServer: str = SMTPSERVERGYD
        self.smtpPort: int = SMTPPORTGYD
        with open(MAILDATA, 'r') as file:
            senderUsername, senderPassword = file.readline().strip().split(',')
        self.mailSender: MailSender = MailSender(senderUsername=senderUsername, 
                                                 senderPassword=senderPassword, 
                                                 smtpServer=self.smtpServer, 
                                                 smtpPort=self.smtpPort)
        self.username: str = senderUsername
        self.password: str = senderPassword
        self.localTimezone = pytz.timezone('America/Santiago')

    def main(self):
        sacRequests: SACRequests = self.getEmails()
        self.processRequests(sacRequests=sacRequests)
        self.sendSummary()
        deleteFileIfExists(PLPREQUESTSPATH)

    def sendSummary(self):
        self.mailSender.sendPLPSummary()

    def touchSolicitudesFile(self):
        if os.path.exists('Solicitudes.xlsa'):
            return
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        headers = ['Timestamp', 'Emisor', 'Asunto', 'TipoSolicitud', 'DeudorNombreCompleto', 'RUTDeudor', 'IdMapsa', 'EstadoAnterior', 'EstadoActual']
        for colNum, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=colNum)
            cell.value = header
        workbook.save(PLPREQUESTSPATH)
        
    def decodeHeader(self, text: str) -> str:
        decodedParts = email.header.decode_header(text)
        decodedSubject = ''
        for part, encoding in decodedParts:
            if isinstance(part, bytes):
                decodedSubject += part.decode(encoding or 'utf-8')
            else:
                decodedSubject += part
        return decodedSubject
    
    def convertToLocalTime(self, timeString: str) -> datetime:
        localTimezone = pytz.timezone('America/Santiago')
        formatString = "%a, %d %b %Y %H:%M:%S %z (%Z)"
        dt = datetime.strptime(timeString, formatString)
        dt = dt.astimezone(localTimezone)
        return dt
    
    def isPLPRequest(self, subject: str) -> bool:
        return any(keyWord in subject for keyWord in SOLICITUD_PLP_KEYWORDS) and PLP in subject

    def isPLPBreached(self, subject: str) -> bool:
        return any(keyWord in subject for keyWord in PLP_INCUMPLIDO_KEYWORDS)
    
    def isDateFormat(self, word: str) -> bool:
        try:
            datetime.strptime(word, '%d-%m-%Y')
            return True
        except Exception:
            return False
    
    def getDeudoresFromPLPBreachedContent(self, content: str) -> list[Deudor]:
        deudores: list[Deudor] = []

        start = re.search(r'PLP_SECUENCIA', content)
        if not start:
            return None
        end = re.findall(r'PLP[1-9]', content)
        if not end:
            return None
        lastEnd = content.rfind(end[-1])
        croppedContent: str = content[start.start() + 14:lastEnd + 4]

        tokens: list[str] = list(filter(lambda elem: elem, croppedContent.split('\n')))
        rawNames: list[str] = []
        for index, element in enumerate(tokens):
            if self.isDateFormat(element):
                rawNames.append(tokens[index - 2])
        for rawName in rawNames:
            tokenizedName: list[str] = list(filter(lambda word: word and not word.isdigit(), rawName.split(' ')))
            apellidoDeudor: str = ''
            nombreDeudor: str = ''
            if len(tokenizedName) == 2:
                apellidoDeudor = tokenizedName[1]
                nombreDeudor = tokenizedName[0]
            elif len(tokenizedName) >= 3:
                apellidoDeudor = f'{tokenizedName[-2]} {tokenizedName[-1]}'
                nombreDeudor = ' '.join(tokenizedName[0:len(tokenizedName)-2])
            deudor: Deudor = Deudor(rawName=rawName, apellidoDeudor=apellidoDeudor, nombreDeudor=nombreDeudor)
            deudores.append(deudor)
        return deudores

    def getEmails(self) -> SACRequests:
        imap = imaplib.IMAP4_SSL(self.smtpServer)
        imap.login(self.username, self.password)
        imap.select("Inbox")
        sinceDate: str = datetime.now().strftime("%d-%b-%Y")
        _, msgnums = imap.search(None, f'(SINCE {sinceDate})')

        plpRequests: list[PLPRequest] = []
        plpBreachedRequests: list[PLPBreached] = []

        for msgnum in msgnums[0].split():
            _, data = imap.fetch(msgnum, '(RFC822)')
            message: Message = email.message_from_bytes(data[0][1])
            messageSender: str = self.decodeHeader(message.get('From'))
            messageDate: str = message.get('Date')
            messageSubject: str = self.decodeHeader(message.get('Subject'))
            print(messageSubject)

            if self.isPLPRequest(messageSubject):
                gydEmail: GYDEmail = GYDEmail(sender=messageSender,
                                              subject=messageSubject,
                                              date=messageDate)
                rutDeudor: str = correctRUTFormat(messageSubject)
                casos: list[Caso] = self.sacConnector.getPossibleMapsaCasos(rutDeudor=rutDeudor, active=False)
                caso: Caso = None
                if len(casos) == 1:
                    caso: Caso = casos[0]
                plpRequest: PLPRequest = PLPRequest(payload=gydEmail,
                                                    rutDeudor=rutDeudor,
                                                    caso=caso)
                plpRequests.append(plpRequest)

            elif self.isPLPBreached(messageSubject.upper()):
                gydEmail: GYDEmail = GYDEmail(sender=messageSender,
                                              subject=messageSubject,
                                              date=messageDate)
                messageString: str = ''
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        messageString += part.as_string()

                deudoresFound: list[Deudor] = self.getDeudoresFromPLPBreachedContent(content=messageString)
                plpBreachedRequest: PLPBreached = PLPBreached(payload=gydEmail, deudores=deudoresFound)
                plpBreachedRequests.append(plpBreachedRequest)

        sacRequests: SACRequests = SACRequests(plpRequests=plpRequests, plpBreachedRequests=plpBreachedRequests)
        imap.close()
        return sacRequests
    
    def processRequests(self, sacRequests: SACRequests):
        self.touchSolicitudesFile()
        processedPLPRequests: list[PLPRequest] = self.processPLPRequests(sacRequests.plpRequests)
        processedPLPBreachedRequests: list[PLPBreached] = self.processPLPBreachedRequests(sacRequests.plpBreachedRequests)
        data = []
        for plpRequest in processedPLPRequests:
            if plpRequest.caso:
                data.append([plpRequest.payload.date, 
                             plpRequest.payload.sender, 
                             plpRequest.payload.subject, 
                             'Solicitud PLP', 
                             plpRequest.caso.nombreDeudor + ' ' + plpRequest.caso.apellidoDeudor, 
                             plpRequest.rutDeudor, 
                             plpRequest.caso.idMapsa, 
                             plpRequest.caso.nombreEstadoAnterior, 
                             plpRequest.caso.nombreEstado])
            else:
                data.append([plpRequest.payload.date, 
                             plpRequest.payload.sender, 
                             plpRequest.payload.subject, 
                             'Solicitud PLP', 
                             'No encontrado', 
                             plpRequest.rutDeudor, 
                             'No encontrado', 
                             'No encontrado', 
                             'No encontrado'])
            
        for plpBreachedRequest in processedPLPBreachedRequests:
            data.append([plpBreachedRequest.payload.date, 
                         plpBreachedRequest.payload.sender,
                         plpBreachedRequest.payload.subject,
                         'PLP Incumplido',
                         '',
                         '',
                         '',
                         '',
                         ''])
            deudor: Deudor
            for deudor in plpBreachedRequest.deudores:
                if deudor.casoAsociado:
                    data.append(['',
                                 '',
                                 '',
                                 '',
                                 deudor.rawName,
                                 deudor.casoAsociado.rutDeudor,
                                 deudor.casoAsociado.idMapsa,
                                 deudor.casoAsociado.nombreEstadoAnterior,
                                 deudor.casoAsociado.nombreEstado
                                 ])
                else:
                    data.append(['',
                                 '',
                                 '',
                                 '',
                                 deudor.rawName,
                                 'No encontrado',
                                 'No encontrado',
                                 'No encontrado',
                                 'No encontrado',
                                 ])
        workbook = openpyxl.load_workbook(PLPREQUESTSPATH)
        worksheet = workbook.active
        for rowData in data:
            worksheet.append(rowData)
        workbook.save(PLPREQUESTSPATH)
            
    def processPLPRequests(self, plpRequests: list[PLPRequest]) -> list[PLPRequest]:
        plpRequest: PLPRequest
        processedPLPRequests: list[PLPRequest] = []
        for plpRequest in plpRequests:
            rutDeudor: str = plpRequest.rutDeudor
            casos: list[Caso] = self.sacConnector.getPossibleMapsaCasos(rutDeudor=rutDeudor, active=False)
            if len(casos) == 1:
                caso: Caso = casos[0]
                plpRequest.caso = caso
                if plpRequest.caso.nombreEstado.upper() != SUSPENDIDO:
                    self.sacConnector.setMapsaCasoState(idMapsa=caso.idMapsa, newState=SUSPENDIDO.lower().capitalize())
                    plpRequest.caso.nombreEstado = SUSPENDIDO.lower().capitalize()
            processedPLPRequests.append(plpRequest)
        return processedPLPRequests
    
    def processPLPBreachedRequests(self, plpBreachedRequests: list[PLPBreached]) -> list[PLPBreached]:
        plpBreachedRequest: PLPBreached
        processedPLPBreachedRequests: list[PLPBreached] = []
        for plpBreachedRequest in plpBreachedRequests:
            deudor: Deudor
            mappedDeudores: list[Deudor] = []
            for deudor in plpBreachedRequest.deudores:
                casos: list[Caso] = self.sacConnector.getPossibleMapsaCasos(apellidoDeudor=deudor.apellidoDeudor, nombreDeudor=deudor.nombreDeudor, active=False)
                if len(casos) == 1:
                    caso: Caso = casos[0]
                    deudor.casoAsociado = caso
                    if caso.nombreEstado.upper() != ACTIVO:
                        self.sacConnector.setMapsaCasoState(idMapsa=caso.idMapsa, newState=ACTIVO.lower().capitalize())
                        deudor.casoAsociado.nombreEstado = ACTIVO.lower().capitalize()
                mappedDeudores.append(deudor)
            plpBreachedRequest.deudores = mappedDeudores
            processedPLPBreachedRequests.append(plpBreachedRequest)
        return processedPLPBreachedRequests
                        


                    






                
            
            

        

    



    