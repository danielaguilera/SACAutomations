from fpdf import FPDF
from ReporteData import ReporteData
from GlobalFunctions import *
from Servicio import Servicio

class PDFGenerator:
    def __init__(self):
        pass
        
    def generateReporte(self, reporteData: ReporteData):
        contactoReporte : str = reporteData.destinatario.nombreDestinatario
        prefijo: str = contactoReporte[0: contactoReporte.find('.') + 1]
        encabezado: str = contactoReporte[contactoReporte.find('.') + 2::]
        
        pdf: FPDF = FPDF('P', 'mm', 'Letter')

        pdf.add_page()
        pdf.set_font('helvetica', 'BI', 10)
        pdf.set_text_color(0, 0, 255)
        pdf.set_xy(x=130, y=10)
        pdf.cell(40, 10, transformDateToSpanish(date=datetime.now()))
        pdf.image('Images/Logo.PNG', x=18, y=15, w=60, h=20)

        pdf.set_xy(x=18, y=40)
        pdf.set_font('Times', 'BI', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(40, 10, prefijo)
        pdf.set_xy(x=18, y=48)
        pdf.cell(40, 10, encabezado)
        pdf.set_xy(x=18, y=56)
        pdf.cell(40, 10, 'MV SA')
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
        pdf.cell(40, 10, reporteData.beneficiario.nombreBeneficiario)
        pdf.set_xy(x=140, y=90)
        pdf.set_font(size=13, family='Arial')
        pdf.cell(40, 10, 'RUT')
        pdf.set_font(size=14, family='Arial')
        pdf.set_xy(x=155, y=90)
        pdf.cell(40, 10, reporteData.beneficiario.rutBeneficiario)

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

        pdf.line(x1=18, y1=108, x2=190, y2=108)

        columnaFactura : Servicio
        delta = 13
        pdf.set_font(size=11, family='Arial')
        pdf.set_text_color(0, 0, 0)
        for index, columnaFactura in enumerate(reporteData.servicios):
            pdf.set_xy(x=18, y=106 + index*delta)
            pdf.cell(40, 10, columnaFactura.rutDeudor)
            pdf.set_font(size=9, family='Arial')
            pdf.set_xy(x=45, y=106 + index*delta)
            pdf.cell(40, 10, columnaFactura.apellidoDeudor)
            pdf.set_xy(x=80, y=106 + index*delta)
            pdf.cell(40, 10, columnaFactura.nombreDeudor)
            pdf.set_font(size=11, family='Arial')
            pdf.set_xy(x=115, y=106 + index*delta)
            pdf.cell(40, 10, str(columnaFactura.boleta))
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
            pdf.set_font(size=11, family='Arial')
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(x=45, y=112 + index*delta)
            pdf.cell(40, 10, f'{str(columnaFactura.idCliente)}    | {columnaFactura.nombreCliente}')
            pdf.set_xy(x=120, y=112 + index*delta)
            pdf.cell(40, 10, columnaFactura.codigo)
            pdf.line(x1=18, y1=120 + index*delta, x2=190, y2=120 + index*delta)


        pdf.image('Images/Signing.PNG', x=18, y=130 + index*delta, w=140, h=40)        

        pdf.output(f'GeneratedReports/{reporteData.numBoleta}.pdf')
        
            