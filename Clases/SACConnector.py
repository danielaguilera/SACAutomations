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
from Clases.Caso import Caso

class SACConnector:
    def __init__(self):
        pyodbc.pooling = False
        self.connBoleta: pyodbc.Connection = pyodbc.connect(SACBOLETASPATH)
        self.connData: pyodbc.Connection = pyodbc.connect(SACDATAPATH)
        self.cursorBoleta: pyodbc.Cursor = self.connBoleta.cursor()
        self.cursorBoleta.fast_executemany = True
        self.cursorData: pyodbc.Cursor = self.connData.cursor()
        self.cursorData.fast_executemany = True
        
        self.beneficiariosTable: str = 'Beneficiarios'
        self.clientesTable: str = 'Tabla_Clientes'
        self.mapsaTable: str = 'Mapsa'
        self.boletasTable: str = 'Tabla_nueva_de_boletas'
        self.gastosTable: str = 'ITEM_Gastos'
        
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
            fechaBoleta : datetime = dataReceived[2]
            if fechaBoleta.year != self.year:
                continue
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
            codigoBoleta: str = dataReceived[9] if dataReceived[9] else ''

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
        
    def getAllClientes(self) -> list[Cliente]:
        clientesData: list[Cliente] = []
        self.cursorData.execute(f'''
                                    SELECT IdCliente, Cliente
                                    FROM {self.clientesTable}
                                ''')
        for data in self.cursorData.fetchall():
            idCliente, nombreCliente = data
            clientesData.append(Cliente(idCliente=idCliente, nombreCliente=nombreCliente))
        return clientesData
    
    def getAllCodigos(self) -> list[str]:
        codigosData: list[str] = []
        self.cursorData.execute(f'''
                                    SELECT ITEM
                                    FROM {self.gastosTable}
                                ''')
        for data in self.cursorData.fetchall():
            codigosData.append(data[0])
        return codigosData
    
    def getPossibleMapsaCasos(self, rutDeudor: str = None, idCliente: int = None) -> list[Caso]:
        casosFound : list[Caso] = []
        if rutDeudor and idCliente:
            query: str = f'''
                        SELECT IdMapsa, Estado, Asignado, Bsecs, "Apellido Deudor", "RUT Deudor", Cliente, 
                        FROM {self.mapsaTable}
                        WHERE "RUT Deudor" LIKE '%{rutDeudor}%' AND Cliente = {idCliente}
                        '''
        elif rutDeudor and not idCliente:
            query: str = f'''
                            SELECT IdMapsa, Estado, Asignado, Bsecs, "Apellido Deudor", "RUT Deudor"
                            FROM {self.mapsaTable}
                            WHERE "RUT Deudor" LIKE '{rutDeudor}%'
                        '''
                        
        elif idCliente and not rutDeudor:
            query: str = f'''
                            SELECT IdMapsa, Estado, Asignado, Bsecs, "Apellido Deudor", "RUT Deudor"
                            FROM {self.mapsaTable}
                            WHERE Cliente = {idCliente}
                        '''
        else:
            return []
        self.cursorData.execute(query)
        for data in self.cursorData.fetchall():
            idMapsa, nombreEstado, fechaAsignado, bsecs, apellidoDeudor, rutDeudor = data
            casosFound.append(Caso(idMapsa=idMapsa, 
                                   nombreEstado=nombreEstado, 
                                   fechaAsignado=fechaAsignado, 
                                   bsecs=bsecs, 
                                   rutDeudor=rutDeudor,
                                   apellidoDeudor=apellidoDeudor))
        return casosFound

    def insertBoletaData(self):
        self.cursorBoleta.execute(f'''
                                  INSERT INTO Tabla_nueva_de_boletas (IdBoleta, Numero, Fecha, Monto, Nota, Print, Mes, "RUT Beneficiario")
                                  VALUES (1111, 1111, '21-mar.-23' , '77777', 'Test Daniel', False, 'abr./2023', '19.618.378-7')                              
                                  ''')
        self.connBoleta.commit()
        
    def getBoletaData(self):
        self.cursorBoleta.execute(f'''
                                  SELECT * FROM Tabla_nueva_de_boletas
                                  WHERE IdBoleta = 1111''')
        print(self.cursorBoleta.fetchall())
            
        