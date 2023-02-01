import pyodbc
import sys
from fpdf import FPDF
from datetime import datetime
from BillingColumn import BillingColumn
import requests

numBoleta : int = 6110

def transformDateToSpanish(date : datetime) -> str:
    weekDays = {0: 'lunes', 1: 'martes', 2:'miércoles', 3:'jueves', 4:'viernes', 5:'sábado', 6:'domingo'}
    monthNames = {1: 'enero', 2: 'febrero', 3:'marzo', 4:'abril', 5:'mayo', 6:'junio', 7:'julio', 8:'agosto', 9:'septiembre', 10:'octubre', 11:'noviembre', 12:'diciembre'}
    return f'{weekDays[date.weekday()]}, {date.day} de {monthNames[date.month]} de {date.year}'

def transformDateToSpanishBrief(date : datetime) -> str:
    monthNames = {1: 'ene', 2: 'feb', 3:'mar', 4:'abr', 5:'may', 6:'jun', 7:'jul', 8:'ago', 9:'sep', 10:'oct', 11:'nov', 12:'dic'}
    return f'{date.day}-{monthNames[date.month]}-{str(date.year)[2::]}'


if __name__ == '__main__':

    # Gathering data from SAC Boletas
    connBoleta = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\daguilera\Desktop\SAC\SAC Boletas.accdb;")
    cursorBoleta = connBoleta.cursor()
    cursorBoleta.execute(f"SELECT * FROM Tabla_nueva_de_boletas WHERE Numero = {numBoleta}")

    columnasFactura : list[BillingColumn] = []

    for dataReceived in cursorBoleta.fetchall(): 
        rutBeneficiario = dataReceived[7]
        idBoleta = dataReceived[0]
        montoBoleta = int(dataReceived[3])
        fechaBoleta = dataReceived[2]
        notaBoleta = dataReceived[4]
        codigoBoleta = dataReceived[9]

        # Gathering data from SAC Data
        connData = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\daguilera\Desktop\SAC\SAC Data.accdb;")
        cursorData = connData.cursor()
        cursorData.execute(f'SELECT "Apellido Deudor", "Rut Deudor", Cliente FROM Mapsa WHERE IdMapsa = {idBoleta}')
        apellidoDeudor, rutDeudor, idCliente = list(cursorData.fetchall())[0]
        cursorData.execute(f'SELECT Cliente FROM "Tabla Clientes" WHERE IdCliente = {idCliente}')
        nombreCliente = list(cursorData.fetchall())[0][0]
        query = '''
                    SELECT "Nombre o Razón Social" 
                    FROM Beneficiarios
                    WHERE "RUT Beneficiario" LIKE '%{}%'
                '''.format(rutBeneficiario)
        cursorData.execute(query)
        nombreBeneficiario = list(cursorData.fetchall())[0][0]

        nombreResponse = requests.get('https://api.libreapi.cl/rut/activities', params = {'rut': f'{rutDeudor}'} ).json()
        nombreDeudor = nombreResponse['data']['name'] if nombreResponse['status'] == 'success' else ''
        nombreDeudorToList = nombreDeudor.strip().split(' ')
        print(nombreDeudor)
        if len(nombreDeudorToList) == 3:
            nombreDeudor = nombreDeudorToList[0]
        elif len(nombreDeudorToList) == 4:
            nombreDeudor = ' '.join(nombreDeudorToList[0:2])

        # Print data in console:
        print(f'Fecha boleta: {fechaBoleta}')
        print(f'Rut beneficiario: {rutBeneficiario}')
        print(f'Id Boleta: {idBoleta}')
        print(f'Monto boleta: {montoBoleta}')
        print(f'Nota boleta: {notaBoleta}')
        print(f'Código boleta: {codigoBoleta}')
        print(f'Nombre deudor: {nombreDeudor}')
        print(f'Apellido deudor: {apellidoDeudor}')
        print(f'Rut deudor: {rutDeudor}')
        print(f'Id Cliente: {idCliente}')
        print(f'Nombre cliente: {nombreCliente}')
        print(f'Nombre beneficiario: {nombreBeneficiario}')
        print('----------------------------------------------\n')

        # Append column object:
        columna : BillingColumn = BillingColumn(rutDeudor=rutDeudor, apellidoDeudor=apellidoDeudor, nombreDeudor=nombreDeudor, idCliente=str(idCliente), nombreCliente=nombreCliente, boleta=str(numBoleta), fecha=transformDateToSpanishBrief(fechaBoleta), monto=str(montoBoleta), nota=notaBoleta if notaBoleta else '', codigo=codigoBoleta)
        columnasFactura.append(columna)

    # Generating PDF
    pdf = FPDF('P', 'mm', 'Letter')
    pdf.add_page()
    pdf.set_font('helvetica', 'BI', 10)
    pdf.set_text_color(0, 0, 255)
    pdf.set_xy(x=130, y=10)
    pdf.cell(40, 10, transformDateToSpanish(date=datetime.now()))
    pdf.image('Images/Logo.PNG', x=18, y=15, w=60, h=20)

    pdf.set_xy(x=18, y=40)
    pdf.set_font('Times', 'BI', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(40, 10, 'Sra.')
    pdf.set_xy(x=18, y=48)
    pdf.cell(40, 10, 'Valeria Lara')
    pdf.set_xy(x=18, y=56)
    pdf.cell(40, 10, 'MV SA')
    pdf.set_xy(x=18, y=64)
    pdf.cell(40, 10, 'Presente')
    pdf.set_xy(x=18, y=75)
    pdf.cell(40, 10, 'Sírvase tener por acompañadas, las siguientes boletas por los servicios que en cada caso se señala, así')
    pdf.set_xy(x=18, y=80)
    pdf.cell(40, 10, 'como los antecedentes que las justifican en cada caso.')
    
    pdf.set_xy(x=18, y=90)
    pdf.set_font(size=13)
    pdf.cell(40, 10, 'Beneficiario')
    pdf.set_font(size=11)
    pdf.set_xy(x=50, y=90)
    pdf.cell(40, 10, nombreBeneficiario)
    pdf.set_xy(x=140, y=90)
    pdf.set_font(size=13)
    pdf.cell(40, 10, 'RUT')
    pdf.set_font(size=14)
    pdf.set_xy(x=155, y=90)
    pdf.cell(40, 10, rutBeneficiario)

    pdf.set_font('helvetica', 'BI', 10)
    pdf.set_text_color(0, 0, 255)

    pdf.set_xy(x=18, y=100)
    pdf.cell(40, 10, 'RUT Deudor')
    pdf.set_xy(x=45, y=100)
    pdf.cell(40, 10, 'Apellido Deudor')
    pdf.set_xy(x=85, y=100)
    pdf.cell(40, 10, 'Nombre Deudor')
    pdf.set_xy(x=115, y=100)
    pdf.cell(40, 10, 'Boleta')
    pdf.set_xy(x=130, y=100)
    pdf.cell(40, 10, 'Fecha')
    pdf.set_xy(x=150, y=100)
    pdf.cell(40, 10, 'Monto')
    pdf.set_xy(x=170, y=100)
    pdf.cell(40, 10, 'Nota')

    pdf.line(x1=18, y1=108, x2=190, y2=108)

    columnaFactura : BillingColumn
    delta = 13
    pdf.set_font(size=11)
    pdf.set_text_color(0, 0, 0)
    for index, columnaFactura in enumerate(columnasFactura):
        pdf.set_xy(x=18, y=106 + index*delta)
        pdf.cell(40, 10, columnaFactura.rutDeudor)
        pdf.set_xy(x=45, y=106 + index*delta)
        pdf.cell(40, 10, columnaFactura.apellidoDeudor)
        pdf.set_xy(x=85, y=106 + index*delta)
        pdf.cell(40, 10, columnaFactura.nombreDeudor)
        pdf.set_xy(x=115, y=106 + index*delta)
        pdf.cell(40, 10, columnaFactura.boleta)
        pdf.set_xy(x=130, y=106 + index*delta)
        pdf.cell(40, 10, columnaFactura.fecha)
        pdf.set_xy(x=150, y=106 + index*delta)
        pdf.cell(40, 10, f'${columnaFactura.monto}')
        pdf.set_xy(x=170, y=106 + index*delta)
        pdf.cell(40, 10, columnaFactura.nota)
        pdf.set_text_color(0, 0, 255)
        pdf.set_font('helvetica', 'BI', 10)
        pdf.set_xy(x=18, y=112 + index*delta)
        pdf.cell(40, 10, 'Cliente: ')
        pdf.set_xy(x=105, y=112 + index*delta)
        pdf.cell(40, 10, 'Código: ')
        pdf.set_font(size=11)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(x=45, y=112 + index*delta)
        pdf.cell(40, 10, f'{str(columnaFactura.idCliente)}    | {columnaFactura.nombreCliente}')
        pdf.set_xy(x=120, y=112 + index*delta)
        pdf.cell(40, 10, columnaFactura.codigo)
        pdf.line(x1=18, y1=120 + index*delta, x2=190, y2=120 + index*delta)


    pdf.image('Images/Signing.PNG', x=18, y=130 + index*delta, w=140, h=40)        

    pdf.output(f'GeneratedReports/{numBoleta}.pdf')

    # for row in cursor.fetchall():
    #     print (row)
    #     break

