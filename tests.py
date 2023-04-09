from Clases.SACConnector import SACConnector
from Utils.GlobalFunctions import *
from datetime import *

# now = datetime.now()
# print(transformDateToSpanishBrief(now, point=True))
# print(getFormattedMonthFromDate(now))

conn = SACConnector()

# query = '''
#             SELECT "Nombre o Razón Social" 
#             FROM Beneficiarios
#             WHERE "RUT Beneficiario" LIKE '%6.698.158-4%'
#         '''
# print(conn.cursorData.execute(query).fetchall())

conn.clearAllBoletaData()

# print(conn.getBeneficiarioData(numBoleta=3643))
# conn.insertBoletaDataExample()

