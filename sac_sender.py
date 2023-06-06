from Clases.SACSenderJob import SACSenderJob
from Utils.Metadata import *
from tkinter import messagebox
import logging

if __name__ == '__main__':
    if not os.path.exists(LOGPATH):
        os.mkdir(LOGPATH)
    logging.basicConfig(filename=SENDER_ERRORS, level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger=logging.getLogger(__name__)
    try:
        sacSenderjob: SACSenderJob = SACSenderJob()
        sacSenderjob.sendReports()
    except Exception as e:
        logger.error(e)
        messagebox.showerror(title='Error', message='Un error detuvo la aplicación. Se reportará en el logger.')
    
    
    
        



