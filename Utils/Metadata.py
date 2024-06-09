import os
from datetime import timedelta

with open('Params/Params.txt', 'r') as file:
    USER, SEND, LANGUAGE, SAC_PATH, SACDATAFILE, SACBOLETASFILE, SACGESTIONESFILE = [line.strip() for line in file.readlines()]

SACDATAPATH: str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + SACDATAFILE + ";"
SACBOLETASPATH: str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + SACBOLETASFILE + ";"
SACGESTIONESPATH: str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + SACGESTIONESFILE + ";"

MONTHNAMES: dict[str] = {1: 'enero', 2: 'febrero', 3:'marzo', 4:'abril', 5:'mayo', 6:'junio', 7:'julio', 8:'agosto', 9:'septiembre', 10:'octubre', 11:'noviembre', 12:'diciembre'}
SHORTMONTHNAMES: dict[str] = {1: 'ene', 2: 'feb', 3:'mar', 4:'abr', 5:'may', 6:'jun', 7:'jul', 8:'ago', 9:'sep', 10:'oct', 11:'nov', 12:'dic'}
SHORTMONTHNAMESENGLISH: dict[str] = {1: 'Jan', 2: 'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
WEEKDAYS: dict[str] = {0: 'lunes', 1: 'martes', 2:'miércoles', 3:'jueves', 4:'viernes', 5:'sábado', 6:'domingo'}

LIBREAPIURL: str = 'https://api.libreapi.cl/rut/activities'

GENERATEDREPORTSPATH: str = os.path.abspath(f"{SAC_PATH}/Historial_de_envíos")
DELIVEREDDATAPATH: str = os.path.abspath(f"{SAC_PATH}/boleta_data")
RESULTPATH: str = os.path.abspath(f"{SAC_PATH}/results")
ACTIVITYLOGFILE: str = os.path.abspath(f"{SAC_PATH}/actividad.txt")
LOGPATH: str =  os.path.abspath(f"{SAC_PATH}/LogFiles")
PLPREQUESTSPATH: str = os.path.abspath(f"{SAC_PATH}/Solicitudes.xlsx")
PLPDATEOVERWRITEPATH: str = os.path.abspath(f"{SAC_PATH}/plp_date_overwrite.txt")

LOGOPATH: str = os.path.abspath(f"{SAC_PATH}/Images/Logo.PNG")
SIGNINGPATH: str = os.path.abspath(f"{SAC_PATH}/Images/Signing.PNG")

LOCKFILEPATH: str = os.path.abspath(f"{SAC_PATH}/temp.lock")

ANEXO: str = 'Anexo'
BOLETA: str = 'Boleta'
REPORTE: str = 'Reporte'

MAILDATA: str = 'Params/mail_data.txt'

SMTPSERVER: str = 'smtp-mail.outlook.com'
SMTPPORT: int = 587

SMTPSERVERGYD: str = 'mail.gydabogados.cl'
SMTPPORTGYD: int = 465

DUARTE: str = 'DUARTE SPA'
GYD: str = 'SERVICIOS JURIDICOS GAUSE'
FACTURAKEYPHRASE: str = 'FACTURA NO AFECTA O EXENTA ELECTRONICA'

SOLICITUD_PLP_KEYWORDS: list[str] = ['SOLICITUD', 'SOLICITO', 'SOLICITAMOS', 'SOLICITADO', 'SOLICITARE', 'SOLICITAREMOS', 'SOLICITE']
PLP_INCUMPLIDO_KEYWORDS: list[str] = ['INCUMPLIDO', 'INCUMPLIO', 'INCUMPLE']
PLP: str = 'PLP'
PLPINCUMPLIDO: str = 'PLP Incumplido'
SOLICITUDPLP: str = 'Solicitud PLP'
PLPBREACHED: str = 'PLPBREACHED'

SOLICITUD_CONTINUAR: str = 'CONTINUAR COB JUD'
SOLICITUD_RETIRAR: str = 'RETIRAR COB JUD'
SOLICITUD_SUSPENDER: str = 'SUSPENDER COB JUD'
JUDICIAL_COLLECTION_KEYWORDS: list[str] = [SOLICITUD_CONTINUAR, SOLICITUD_RETIRAR, SOLICITUD_SUSPENDER]

RUTDEUDOR: int = 0
APELLIDODEUDOR: int = 1
NOMBREDEUDOR: int = 2

ACTIVO: str = 'ACTIVO'
SUSPENDIDO: str = 'SUSPENDIDO'
FINALIZADO: str = 'FINALIZADO'
REINICIADO: str = 'REINICIADO'

PLPREQUESTCODE: str = '200.- Suspendido'
PLPBREACHEDCODE: str = '201.- Reiniciado'
FINISHEDCODE: str = '198.- Terminado/Finalizado'

SENDING_ACTIVITY: str = 'sending'
DELETING_ACTIVITY: str = 'deleting'
ADDING_ACTIVITY: str = 'adding'
VISUALIZING_ACTIVITY: str = 'visualizing'

JUDICIAL_COLLECTION_STATES: dict[str] = {SOLICITUD_CONTINUAR: ACTIVO, SOLICITUD_RETIRAR: FINALIZADO, SOLICITUD_SUSPENDER: SUSPENDIDO}
JUDICIAL_COLLECTION_ACTIONS: dict[str] = {SOLICITUD_CONTINUAR: PLPBREACHEDCODE, SOLICITUD_RETIRAR: FINISHEDCODE, SOLICITUD_SUSPENDER: PLPREQUESTCODE}

MIN_REQUEST_REPETITION_DELAY: int = 15

MATRIX_COLORS = {
    'A': 'D9D9D9',
    'B': 'FFFFCC',
    'C': 'FDE9D9',
    'D': 'DDD9C4',
    'E': 'FCD5B4',
    'F': 'EBF1DE',
    'G': 'C5D9F1'
}

RED = 'C0504D'
SKY_BLUE = 'C5D9F1'
WHITE = 'FFFFFF'
BLACK = '000000'
YELLOW = 'FFC000'
BLUE = '0070C0'