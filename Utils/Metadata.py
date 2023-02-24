SACDATAPATH: str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\User\Desktop\SAC\SAC Data.accdb;"
SACBOLETASPATH: str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\User\Desktop\SAC\SAC Boletas.accdb;"

MONTHNAMES: dict[str] = {1: 'enero', 2: 'febrero', 3:'marzo', 4:'abril', 5:'mayo', 6:'junio', 7:'julio', 8:'agosto', 9:'septiembre', 10:'octubre', 11:'noviembre', 12:'diciembre'}
SHORTMONTHNAMES: dict[str] = {1: 'ene', 2: 'feb', 3:'mar', 4:'abr', 5:'may', 6:'jun', 7:'jul', 8:'ago', 9:'sep', 10:'oct', 11:'nov', 12:'dic'}
WEEKDAYS: dict[str] = {0: 'lunes', 1: 'martes', 2:'miércoles', 3:'jueves', 4:'viernes', 5:'sábado', 6:'domingo'}

LIBREAPIURL: str = 'https://api.libreapi.cl/rut/activities'

GENERATEDREPORTSPATH: str = "ReportesGenerados"
DELIVEREDDATAPATH: str = "DatosRecibidos"
RESULTPATH: str = "Resultados"

LOGOPATH: str = "Images/Logo.PNG"
SIGNINGPATH: str = "Images/Signing.PNG"

ANEXO: str = 'Anexo'
BOLETA: str = 'Boleta'
REPORTE: str = 'Reporte'