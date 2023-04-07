from Clases.SACConnector import SACConnector
from Utils.GlobalFunctions import *
from datetime import *

# now = datetime.now()
# print(transformDateToSpanishBrief(now, point=True))
# print(getFormattedMonthFromDate(now))

conn = SACConnector()
conn.clearAllBoletaData()
# conn.insertBoletaDataExample()