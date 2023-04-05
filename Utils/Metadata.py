import os

ENV: str = 'TST'

SACDATAPATH_PROD: str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\User\Desktop\SAC\SAC Data.accdb;"
SACBOLETASPATH_PROD: str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\User\Desktop\SAC\SAC Boletas.accdb;"

SACDATAPATH_TEST: str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\User\Desktop\SAC_TST\SAC Data.accdb;"
SACBOLETASPATH_TEST: str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\User\Desktop\SAC_TST\SAC Boletas.accdb;"

SACDATAPATH: str = SACDATAPATH_TEST if ENV == 'TST' else SACDATAPATH_PROD
SACBOLETASPATH: str = SACBOLETASPATH_TEST if ENV == 'TST' else SACBOLETASPATH_PROD

MONTHNAMES: dict[str] = {1: 'enero', 2: 'febrero', 3:'marzo', 4:'abril', 5:'mayo', 6:'junio', 7:'julio', 8:'agosto', 9:'septiembre', 10:'octubre', 11:'noviembre', 12:'diciembre'}
SHORTMONTHNAMES: dict[str] = {1: 'ene', 2: 'feb', 3:'mar', 4:'abr', 5:'may', 6:'jun', 7:'jul', 8:'ago', 9:'sep', 10:'oct', 11:'nov', 12:'dic'}
WEEKDAYS: dict[str] = {0: 'lunes', 1: 'martes', 2:'miércoles', 3:'jueves', 4:'viernes', 5:'sábado', 6:'domingo'}

LIBREAPIURL: str = 'https://api.libreapi.cl/rut/activities'

GENERATEDREPORTSPATH: str = os.path.abspath("ReportesGenerados")
DELIVEREDDATAPATH: str = os.path.abspath("DatosRecibidos")
RESULTPATH: str = os.path.abspath("Resultados")

LOGOPATH: str = os.path.abspath("Images/Logo.PNG")
SIGNINGPATH: str = os.path.abspath("Images/Signing.PNG")

ANEXO: str = 'Anexo'
BOLETA: str = 'Boleta'
REPORTE: str = 'Reporte'

MAILDATA: str = 'MailData/SenderData.txt'

SMTPSERVER: str = 'smtp-mail.outlook.com'
SMTPPORT: int = 587

DUARTE: str = 'DUARTE SPA'