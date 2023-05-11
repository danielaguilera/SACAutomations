from Clases.SACSenderJob import SACSenderJob
from tkinter import messagebox
import logging

if __name__ == '__main__':
    logging.basicConfig(filename='Sender_errors.txt', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger=logging.getLogger(__name__)
    try:
        sacSenderjob: SACSenderJob = SACSenderJob()
        sacSenderjob.sendReports()
    except Exception as e:
        logger.error(e)
        messagebox.showerror(title='Error', message='Un error detuvo la aplicación. Se reportará en el logger.')
    
    
    
        



