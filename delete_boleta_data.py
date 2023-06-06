from Clases.SACConnector import SACConnector
from Utils.Metadata import *
from Utils.GlobalFunctions import *

sacConnector: SACConnector = SACConnector()

sacConnector.clearAllBoletaData()
deleteIfExists(RESULTPATH)
deleteIfExists(DELIVEREDDATAPATH)
deleteIfExists(GENERATEDREPORTSPATH)
deleteIfExists(LOGPATH)
deleteFileIfExists(ACTIVITYLOGFILE)