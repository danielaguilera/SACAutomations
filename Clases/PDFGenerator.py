from fpdf import FPDF
from Clases.Resumen import Resumen
from Utils.GlobalFunctions import *
from Clases.Servicio import Servicio
from Utils.Metadata import *
import os
import pandas as pd
import openpyxl
from openpyxl.styles import Alignment

class PDFGenerator:
    def __init__(self):
        pass
        
    def generateReporte(self, resumenBoleta: Resumen):
        contactoReporte : str = resumenBoleta.destinatario.nombreDestinatario
        if contactoReporte.find('.'):
            prefijo: str = contactoReporte[0: contactoReporte.find('.') + 1]
            encabezado: str = contactoReporte[contactoReporte.find('.') + 2::]
        else:
            prefijo: str = ''
            encabezado: str = contactoReporte
        
        pdf: FPDF = FPDF('P', 'mm', 'Letter')

        pdf.add_page()
        pdf.set_font('helvetica', 'BI', 10)
        pdf.set_text_color(0, 0, 255)
        pdf.set_xy(x=130, y=10)
        pdf.cell(40, 10, transformDateToSpanish(date=datetime.now()))
        pdf.image(LOGOPATH, x=18, y=15, w=60, h=20)

        pdf.set_xy(x=18, y=40)
        pdf.set_font('Times', 'BI', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(40, 10, prefijo)
        pdf.set_xy(x=18, y=48)
        pdf.cell(40, 10, encabezado)
        pdf.set_xy(x=18, y=56)
        pdf.cell(40, 10, resumenBoleta.cliente.factura)
        pdf.set_xy(x=18, y=64)
        pdf.cell(40, 10, 'Presente')
        pdf.set_xy(x=18, y=75)
        pdf.cell(40, 10, 'Sírvase tener por acompañadas, las siguientes boletas por los servicios que en cada caso se señala, así')
        pdf.set_xy(x=18, y=80)
        pdf.cell(40, 10, 'como los antecedentes que las justifican en cada caso.')
        
        pdf.set_xy(x=18, y=90)
        pdf.set_font(size=13, family='Arial')
        pdf.cell(40, 10, 'Beneficiario')
        pdf.set_font(size=11, family='Arial')
        pdf.set_xy(x=50, y=90)
        pdf.cell(40, 10, resumenBoleta.beneficiario.nombreBeneficiario)
        pdf.set_xy(x=140, y=90)
        pdf.set_font(size=13, family='Arial')
        pdf.cell(40, 10, 'RUT')
        pdf.set_font(size=14, family='Arial')
        pdf.set_xy(x=155, y=90)
        pdf.cell(40, 10, resumenBoleta.beneficiario.rutBeneficiario)

        pdf.set_font('helvetica', 'BI', 10)
        pdf.set_text_color(0, 0, 255)

        pdf.set_xy(x=18, y=100)
        pdf.cell(40, 10, 'RUT Deudor')
        pdf.set_xy(x=45, y=100)
        pdf.cell(40, 10, 'Apellido Deudor')
        pdf.set_xy(x=80, y=100)
        pdf.cell(40, 10, 'Nombre Deudor')
        pdf.set_xy(x=115, y=100)
        pdf.cell(40, 10, 'Boleta')
        pdf.set_xy(x=130, y=100)
        pdf.cell(40, 10, 'Fecha')
        pdf.set_xy(x=150, y=100)
        pdf.cell(40, 10, 'Monto')
        pdf.set_xy(x=170, y=100)
        pdf.cell(40, 10, 'Nota')

        pdf.line(x1=18, y1=108, x2=200, y2=108)

        servicio : Servicio
        delta = 13
        pdf.set_font(size=11, family='Arial')
        pdf.set_text_color(0, 0, 0)
        for index, servicio in enumerate(resumenBoleta.servicios):
            pdf.set_xy(x=18, y=106 + index*delta)
            pdf.cell(40, 10, resumenBoleta.caso.rutDeudor)
            pdf.set_font(size=9, family='Arial')
            pdf.set_xy(x=45, y=106 + index*delta)
            pdf.cell(40, 10, resumenBoleta.caso.apellidoDeudor)
            pdf.set_xy(x=80, y=106 + index*delta)
            pdf.cell(40, 10, resumenBoleta.caso.nombreDeudor)
            pdf.set_font(size=11, family='Arial')
            pdf.set_xy(x=115, y=106 + index*delta)
            pdf.cell(40, 10, str(resumenBoleta.boleta.numBoleta))
            pdf.set_xy(x=130, y=106 + index*delta)
            pdf.cell(40, 10, transformDateToSpanishBrief(date=resumenBoleta.boleta.fechaEmision))
            pdf.set_xy(x=150, y=106 + index*delta)
            pdf.cell(40, 10, setPriceFormat(servicio.monto))
            pdf.set_xy(x=170, y=106 + index*delta)
            pdf.set_font(size=8, family='Arial')
            pdf.cell(40, 10, servicio.nota)
            pdf.set_text_color(0, 0, 255)
            pdf.set_font('helvetica', 'BI', 10)
            pdf.set_xy(x=18, y=112 + index*delta)
            pdf.cell(40, 10, 'Cliente: ')
            pdf.set_xy(x=105, y=112 + index*delta)
            pdf.cell(40, 10, 'Código: ')
            pdf.set_font(size=11, family='Arial')
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(x=45, y=112 + index*delta)
            pdf.cell(40, 10, f'{str(resumenBoleta.cliente.idCliente)}    | {resumenBoleta.cliente.nombreCliente}')
            pdf.set_xy(x=120, y=112 + index*delta)
            pdf.cell(40, 10, servicio.codigo)
            pdf.line(x1=18, y1=120 + index*delta, x2=200, y2=120 + index*delta)

        pdf.set_xy(x=18, y=120 + index*delta)
        pdf.set_font(size=13, family='Arial')
        pdf.set_text_color(0, 0, 20)
        pdf.cell(40, 10, 'Suma total')
        pdf.set_xy(x=170, y=120 + index*delta)
        pdf.cell(40, 10, setPriceFormat(sum(servicio.monto for servicio in resumenBoleta.servicios)))
        pdf.image(SIGNINGPATH, x=18, y=150 + index*delta, w=140, h=40)        

        if not os.path.exists(f'{DELIVEREDDATAPATH}/{resumenBoleta.destinatario.nombreDestinatario}/{resumenBoleta.boleta.numBoleta}_{resumenBoleta.caso.idMapsa}'):
            os.makedirs(f'{DELIVEREDDATAPATH}/{resumenBoleta.destinatario.nombreDestinatario}/{resumenBoleta.boleta.numBoleta}_{resumenBoleta.caso.idMapsa}')
        pdf.output(f'{DELIVEREDDATAPATH}/{resumenBoleta.destinatario.nombreDestinatario}/{resumenBoleta.boleta.numBoleta}_{resumenBoleta.caso.idMapsa}/Reporte_{resumenBoleta.boleta.numBoleta}.pdf')
        
        print(f'Reporte n°{resumenBoleta.boleta.numBoleta} generado!')
        self.addBoletaDataToExcelMatrix(resumenBoleta=resumenBoleta)
        
    def createExcelMatrix(self, resumenBoleta: Resumen):
        if os.path.exists(f'{DELIVEREDDATAPATH}/{resumenBoleta.destinatario.nombreDestinatario}/Rendicion.xlsx'):
            return
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        headers = [' NOMBRE DEUDOR ', ' OPERACIÓN ', ' FOLIO ', ' ITEM ', ' SERVICIO ', ' RUT PRESTADOR ', ' PRESTADOR ', ' N°DOC ', ' MONTO ', ' N°BOLETA ', ' FECHA PAGO ']
        for colNum, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=colNum)
            cell.value = header
        workbook.save(f'{DELIVEREDDATAPATH}/{resumenBoleta.destinatario.nombreDestinatario}/Rendicion.xlsx')
        
    def addBoletaDataToExcelMatrix(self, resumenBoleta: Resumen):
        if not os.path.exists(f'{DELIVEREDDATAPATH}/{resumenBoleta.destinatario.nombreDestinatario}/Rendicion.xlsx'):
            self.createExcelMatrix(resumenBoleta=resumenBoleta)
        excelMatrixRoot : str = f'{DELIVEREDDATAPATH}/{resumenBoleta.destinatario.nombreDestinatario}/Rendicion.xlsx'
        workbook = openpyxl.load_workbook(excelMatrixRoot)
        sheet = workbook.active
        servicio: Servicio
        try:
           filaNDoc = sheet.cell(row=sheet.max_row, column=8).value + 1
        except Exception:
           filaNDoc = 1
        for servicio in resumenBoleta.servicios:
            filaNombreDeudor = resumenBoleta.caso.apellidoDeudor + ' ' + resumenBoleta.caso.nombreDeudor
            filaOperacion = resumenBoleta.caso.nOperacion
            filaFolio = resumenBoleta.caso.folio
            filaItem = servicio.codigo.split(' ')[0].upper()
            filaServicio = servicio.codigo.upper()
            filaServicio = filaServicio.replace(filaItem, '')
            filaRUTPrestador = resumenBoleta.beneficiario.rutBeneficiario
            filaPrestador = resumenBoleta.beneficiario.nombreBeneficiario
            filaMonto = servicio.monto
            filaNBoleta = resumenBoleta.boleta.numBoleta
            filaFechaPago = resumenBoleta.boleta.fechaEmision.strftime("%d-%m-%Y")
            newRow = [filaNombreDeudor, 
                    filaOperacion, 
                    filaFolio, 
                    filaItem, 
                    filaServicio, 
                    filaRUTPrestador, 
                    filaPrestador, 
                    filaNDoc, 
                    filaMonto, 
                    filaNBoleta, 
                    filaFechaPago]
            sheet.append(newRow)
        
        for column in sheet.columns:
            header = str(column[0].value)
            maxLength = len(header)
            column = [cell for cell in column]
            for cell in column:
                if len(str(cell.value)) > maxLength:
                    maxLength = len(cell.value)
            adjustedWidth = (maxLength + 2)
            sheet.column_dimensions[openpyxl.utils.get_column_letter(cell.column)].width = adjustedWidth
            for cell in column:
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        
        workbook.save(excelMatrixRoot)
        
            
            
        

            