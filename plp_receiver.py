import os
from Utils.Metadata import *
from Clases.SACConnector import SACConnector
from Clases.PLPManager import PLPManager

if __name__ == '__main__':
    plp = PLPManager()
    plp.fetchMailData()