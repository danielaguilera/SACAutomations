from Clases.App import App
from tkinter import messagebox
import logging

if __name__ == '__main__':
    logging.basicConfig(filename='App_errors.txt', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger=logging.getLogger(__name__)
    # try:
    #     app = App()
    # except Exception as e:
    #     logger.error(e)
    #     messagebox.showerror(title='Error', message='Un error detuvo la aplicación. Se reportará en el logger.')
    app = App()