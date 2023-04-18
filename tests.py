from Clases.SACConnector import SACConnector
from Utils.GlobalFunctions import *
from datetime import *
from Clases.Destinatario import Destinatario

conn = SACConnector()

dest: Destinatario
for dest in conn.getAllDestinatarios():
    print(f'{dest.nombreDestinatario} - {dest.correoDestinatario}')
    
print(conn.getDestinatarioByCliente(idCliente=1).nombreDestinatario)


# # now = datetime.now()
# # print(transformDateToSpanishBrief(now, point=True))
# # print(getFormattedMonthFromDate(now))

# conn = SACConnector()

# # query = '''
# #             SELECT "Nombre o Razón Social" 
# #             FROM Beneficiarios
# #             WHERE "RUT Beneficiario" LIKE '%6.698.158-4%'
# #         '''
# # print(conn.cursorData.execute(query).fetchall())

# conn.clearAllBoletaData()

# # print(conn.getBeneficiarioData(numBoleta=3643))
# # conn.insertBoletaDataExample()

# import smtplib, ssl

# sender_email = "servidor@gydabogados.cl"
# receiver_email = "draguilera@uc.cl"
# message = """\
# Subject: It Worked!

# Simple Text email from your Python Script."""

# port = 465  
# app_password = "EstadoGyD@2023"

# context = ssl.create_default_context()

# with smtplib.SMTP_SSL("mail.gydabogados.cl", port, context=context) as server:
#     server.login(sender_email, app_password)
#     server.sendmail(sender_email, receiver_email, message)




# import glob, sys, fitz
# import tkinter as tk
# from PIL import ImageTk, Image

# # To get better resolution
# zoom_x = 1.0  # horizontal zoom
# zoom_y = 1.0  # vertical zoom
# mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

# filename = 'Boleta_3643.pdf'
# doc = fitz.open(filename)  # open document
# for page in doc:  # iterate through the pages
#     pix = page.get_pixmap(matrix=mat)  # render page to an image
#     pix.save("result.png")  # store image as a PNG

# root = tk.Tk()

# # Load the PNG image
# image = Image.open("result.png")
# photo = ImageTk.PhotoImage(image)

# # Create a Label widget and set the image
# label = tk.Label(root, image=photo)
# label.pack()

# root.mainloop()