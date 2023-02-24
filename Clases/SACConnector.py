from Utils.Metadata import *
import pyodbc
import requests
from Clases.Deudor import Deudor
from Clases.Cliente import Cliente
from Clases.Servicio import Servicio
from Clases.Beneficiario import Beneficiario
from Clases.Destinatario import Destinatario
from Clases.ReporteData import ReporteData
from datetime import datetime
from Utils.GlobalFunctions import *

class SACConnector:
    def __init__(self):
        pyodbc.pooling = False
        self.cursorBoleta: pyodbc.Cursor = pyodbc.connect(SACBOLETASPATH).cursor()
        self.cursorBoleta.fast_executemany = True
        self.cursorData: pyodbc.Cursor = pyodbc.connect(SACDATAPATH).cursor()
        self.cursorData.fast_executemany = True
        
        self.beneficiariosTable: str = 'Beneficiarios'
        self.clientesTable:str = 'Tabla_Clientes'
        self.mapsaTable: str = 'Mapsa'
        self.boletasTable: str = 'Tabla_nueva_de_boletas'
        
        self.year: int = 2022 #Hardcoded
        
    def getDeudorData(self, idBoleta: int) -> Deudor | None:
        self.cursorData.execute(f'SELECT "Apellido Deudor", "Rut Deudor", Cliente FROM {self.mapsaTable} WHERE IdMapsa = {idBoleta}')
        apellidoDeudor, rutDeudor, idCliente = list(self.cursorData.fetchall())[0]
        nombreResponse: requests.Response = requests.get(url=LIBREAPIURL, params={'rut': rutDeudor})
        if nombreResponse.status_code == 200:
            nombreDeudor: str = nombreResponse.json()['data']['name']
            nombreDeudorToList: list[str] = list(map(lambda x: x.capitalize(), nombreDeudor.strip().split(' ')))
            if len(nombreDeudorToList) == 3:
                nombreDeudor = nombreDeudorToList[0]
            elif len(nombreDeudorToList) > 3:
                nombreDeudor = ' '.join(nombreDeudorToList[0:2])
            else:
                nombreDeudor = ''
        else:
            nombreDeudor = ''
        return Deudor(apellidoDeudor=apellidoDeudor, nombreDeudor=nombreDeudor, rutDeudor=rutDeudor, idCliente=idCliente)

    def getClienteData(self, idCliente: int) -> Cliente | None:
        self.cursorData.execute(f'SELECT Cliente FROM {self.clientesTable} WHERE IdCliente = {idCliente}')
        nombreCliente = list(self.cursorData.fetchall())[0][0]
        return Cliente(idCliente=idCliente, nombreCliente=nombreCliente)
    
    def getDestinatarioData(self, numBoleta: int) -> Destinatario | None:
        self.cursorBoleta.execute(f"SELECT * FROM {self.boletasTable} WHERE Numero = {numBoleta}")
        for dataReceived in self.cursorBoleta.fetchall(): 
            idBoleta: int = dataReceived[0]
            fechaBoleta : datetime = dataReceived[2]
            if fechaBoleta.year != self.year:
                continue
            deudorData: Deudor = self.getDeudorData(idBoleta=idBoleta)
            idCliente: int = deudorData.idCliente
            break
        
        self.cursorData.execute(f'SELECT Contacto, "Correo Contacto" FROM {self.clientesTable} WHERE IdCliente = {idCliente}')
        nombreDestinatario, correoDestinatario = list(self.cursorData.fetchall())[0]
        return Destinatario(nombreDestinatario=nombreDestinatario, correoDestinatario=correoDestinatario)
    
    def getBeneficiarioData(self, numBoleta: int) -> Beneficiario | None:
        self.cursorBoleta.execute(f"SELECT * FROM {self.boletasTable} WHERE Numero = {numBoleta}")
        for dataReceived in self.cursorBoleta.fetchall(): 
            rutBeneficiario: str = dataReceived[7]
            break
        query = '''
                    SELECT "Nombre o Razón Social" 
                    FROM {}
                    WHERE "RUT Beneficiario" LIKE '%{}%'
                '''.format(self.beneficiariosTable, rutBeneficiario)
        self.cursorData.execute(query)
        nombreBeneficiario = list(self.cursorData.fetchall())[0][0]
        return Beneficiario(nombreBeneficiario=nombreBeneficiario, rutBeneficiario=rutBeneficiario)
    
    def getServicios(self, numBoleta: int) -> list[Servicio] | None:
        self.cursorBoleta.execute(f"SELECT * FROM {self.boletasTable} WHERE Numero = {numBoleta}")
        servicios: list[Servicio] = []
        for dataReceived in self.cursorBoleta.fetchall(): 
            idBoleta: int = dataReceived[0]
            montoBoleta: int = int(dataReceived[3])
            fechaBoleta : datetime = dataReceived[2]
            notaBoleta: str = dataReceived[4]
            codigoBoleta: str = dataReceived[9]

            if fechaBoleta.year != self.year:
                continue
            
            deudorData: Deudor = self.getDeudorData(idBoleta=idBoleta)
            clienteData: Cliente = self.getClienteData(idCliente=deudorData.idCliente)
            servicio : Servicio = Servicio(rutDeudor=deudorData.rutDeudor, 
                                           apellidoDeudor=deudorData.apellidoDeudor, 
                                           nombreDeudor=deudorData.nombreDeudor, 
                                           idCliente=clienteData.idCliente, 
                                           nombreCliente=clienteData.nombreCliente, 
                                           boleta=numBoleta, 
                                           fecha=transformDateToSpanishBrief(fechaBoleta), 
                                           monto=montoBoleta, 
                                           nota=notaBoleta if notaBoleta else '', 
                                           codigo=codigoBoleta)
            servicios.append(servicio)
        return servicios
    
    def getReporteData(self, numBoleta: int) -> ReporteData | None:
        try: 
            destinatario: Destinatario = self.getDestinatarioData(numBoleta=numBoleta)
            beneficiario: Beneficiario = self.getBeneficiarioData(numBoleta=numBoleta)
            servicios: list[Servicio] = self.getServicios(numBoleta=numBoleta)
            return ReporteData(destinatario=destinatario, beneficiario=beneficiario, servicios=servicios, numBoleta=numBoleta)
        except Exception:
            print(f'Datos no encontrados para boleta n°{numBoleta}')
            return
            
        