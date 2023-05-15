from Utils.Metadata import *
import pyodbc
import requests
from Clases.Deudor import Deudor
from Clases.Cliente import Cliente
from Clases.Servicio import Servicio
from Clases.Beneficiario import Beneficiario
from Clases.Destinatario import Destinatario
from Clases.ReporteData import ReporteData
from Clases.Boleta import Boleta
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
        self.clientesTable: str = 'Clientes'
        self.mapsaTable: str = 'Mapsa'
        self.boletasTable: str = 'Boletas'
        self.gastosTable: str = 'ITEM-Gastos'
        
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
    
    def getDeudorName(self, rutDeudor: str):
        try:
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
            return nombreDeudor
        except Exception:
            return ''
        
    def getClienteData(self, idCliente: int) -> Cliente | None:
        self.cursorData.execute(f'SELECT Cliente FROM {self.clientesTable} WHERE IdCliente = {idCliente}')
        nombreCliente = list(self.cursorData.fetchall())[0][0]
        return Cliente(idCliente=idCliente, nombreCliente=nombreCliente)
    
    def getDestinatarioData(self, numBoleta: int, idMapsa : int) -> Destinatario | None:
        self.cursorBoleta.execute(f"SELECT * FROM {self.boletasTable} WHERE Numero = {numBoleta} AND Check = False AND Idboleta = {idMapsa}")
        for dataReceived in self.cursorBoleta.fetchall(): 
            idBoleta: int = dataReceived[0]
            deudorData: Deudor = self.getDeudorData(idBoleta=idBoleta)
            idCliente: int = deudorData.idCliente
            break
        self.cursorData.execute(f'SELECT Contacto, Mail FROM {self.clientesTable} WHERE IdCliente = {idCliente}')
        nombreDestinatario, correoDestinatario = list(self.cursorData.fetchall())[0]
        return Destinatario(nombreDestinatario=nombreDestinatario, correoDestinatario=correoDestinatario)
    
    def getBeneficiarioData(self, numBoleta: int, idMapsa: int) -> Beneficiario | None:
        self.cursorBoleta.execute(f"SELECT * FROM {self.boletasTable} WHERE Numero = {numBoleta} AND Check = False AND Idboleta = {idMapsa}")
        for dataReceived in self.cursorBoleta.fetchall(): 
            rutBeneficiario: str = dataReceived[7]
            fechaBoleta : datetime = dataReceived[2]
            # if fechaBoleta.year != self.year:
            #     continue
            break
        query = '''
                    SELECT "Nombre o Razón Social" 
                    FROM {}
                    WHERE "RUT Beneficiario" LIKE '%{}%'
                '''.format(self.beneficiariosTable, rutBeneficiario)
        self.cursorData.execute(query)
        nombreBeneficiario = list(self.cursorData.fetchall())[0][0]
        return Beneficiario(nombreBeneficiario=nombreBeneficiario, rutBeneficiario=rutBeneficiario)
    
    def getDestinatarioByCliente(self, idCliente: int) -> Destinatario:
        self.cursorData.execute(f'''
                                    SELECT Contacto, Mail
                                    FROM {self.clientesTable}
                                    WHERE IdCliente = {idCliente}
                                ''')
        nombreDestinatario, correoDestinatario = self.cursorData.fetchall()[0]
        return Destinatario(nombreDestinatario=nombreDestinatario, correoDestinatario=correoDestinatario)
    
    def findBeneficiario(self, rutBeneficiario: str) -> Beneficiario | None:
        self.cursorData.execute(f"""SELECT "Nombre o Razón Social" FROM {self.beneficiariosTable} WHERE "RUT Beneficiario" LIKE '%{rutBeneficiario}%'""")
        data = self.cursorData.fetchall()
        if data:
            nombreBeneficiario: str = data[0][0]
            return Beneficiario(rutBeneficiario=rutBeneficiario, nombreBeneficiario=nombreBeneficiario)
        return None
    
    def getPossibleBeneficiarios(self, rutBeneficiario: str) -> list[Beneficiario]:
        beneficiarios: list[Beneficiario] = []
        self.cursorData.execute(f"""SELECT "RUT Beneficiario", "Nombre o Razón Social" FROM {self.beneficiariosTable} WHERE "RUT Beneficiario" LIKE '{rutBeneficiario}%'""")
        for data in self.cursorData.fetchall():
            rutBeneficiarioFound, nombreBeneficiarioFound = data
            beneficiarios.append(Beneficiario(rutBeneficiario=rutBeneficiarioFound, nombreBeneficiario=nombreBeneficiarioFound)) 
        return beneficiarios
        
    def getServicios(self, numBoleta: int, idMapsa: int) -> list[Servicio] | None:
        self.cursorBoleta.execute(f"SELECT * FROM {self.boletasTable} WHERE Numero = {numBoleta} AND Check = False AND Idboleta = {idMapsa}")
        servicios: list[Servicio] = []
        for dataReceived in self.cursorBoleta.fetchall(): 
            idBoleta: int = dataReceived[0]
            montoBoleta: int = int(dataReceived[3])
            fechaBoleta : datetime = dataReceived[2]
            notaBoleta: str = dataReceived[4]
            codigoBoleta: str = dataReceived[9] if dataReceived[9] else ''
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
    
    def getReporteData(self, numBoleta: int, idMapsa: int, destinatarioSet: Destinatario | None = None) -> ReporteData | None:
        if destinatarioSet:
            destinatario: Destinatario = destinatarioSet
        else:
            destinatario: Destinatario = self.getDestinatarioData(numBoleta=numBoleta, idMapsa=idMapsa)
        beneficiario: Beneficiario = self.getBeneficiarioData(numBoleta=numBoleta, idMapsa=idMapsa)
        servicios: list[Servicio] = self.getServicios(numBoleta=numBoleta, idMapsa=idMapsa)
        return ReporteData(destinatario=destinatario, beneficiario=beneficiario, servicios=servicios, numBoleta=numBoleta, idMapsa=idMapsa)
 
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
                                    FROM "{self.gastosTable}"
                                ''')
        for data in self.cursorData.fetchall():
            codigosData.append(data[0])
        return codigosData
    
    def getAllBeneficiarios(self) -> list[Beneficiario]:
        beneficiariosData: list[Beneficiario] = []
        self.cursorData.execute(f'''
                                    SELECT "RUT Beneficiario", "Nombre o Razón Social"
                                    FROM {self.beneficiariosTable}
                                ''')
        for data in self.cursorData.fetchall():
            rutBeneficiario, nombreBeneficiario = data
            beneficiariosData.append(Beneficiario(rutBeneficiario=rutBeneficiario, nombreBeneficiario=nombreBeneficiario))
        return beneficiariosData
    
    def getAllDestinatarios(self) -> list[Destinatario]:
        destinatariosData: list[Destinatario] = []
        self.cursorData.execute(f'''
                                    SELECT DISTINCT Contacto, Mail
                                    FROM {self.clientesTable}
                                ''')
        for data in self.cursorData.fetchall():
            nombreDestinatario, correoDestinatario = data
            destinatariosData.append(Destinatario(nombreDestinatario=nombreDestinatario, correoDestinatario=correoDestinatario))
        return destinatariosData 
    
    def getPossibleMapsaCasos(self, rutDeudor: str = '', apellidoDeudor: str = '', idCliente: int = None) -> list[Caso]:
        casosFound : list[Caso] = []
        query: str = f'''
                        SELECT IdMapsa, Estado, Asignado, Bsecs, "Apellido Deudor", "RUT Deudor", Mapsa.Cliente, Clientes.Cliente
                        FROM {self.mapsaTable}
                        INNER JOIN {self.clientesTable}
                        ON {self.clientesTable}.IdCliente = {self.mapsaTable}.Cliente
                        WHERE
                        Estado LIKE '%Activo%'\n
                    '''
                    
        if idCliente:
            query += f'AND {self.mapsaTable}.Cliente = {idCliente}\n'   
        if rutDeudor:
            query += f"""AND "RUT Deudor" LIKE '{rutDeudor}%'\n"""
        if apellidoDeudor:
            query += f"""AND "Apellido Deudor" LIKE '{apellidoDeudor}%'"""    
        
        self.cursorData.execute(query)
        for data in self.cursorData.fetchall():
            idMapsa, nombreEstado, fechaAsignado, bsecs, apellidoDeudor, rutDeudor, idCliente, nombreCliente = data
            casosFound.append(Caso(idMapsa=idMapsa, 
                                   nombreEstado=nombreEstado, 
                                   fechaAsignado=fechaAsignado, 
                                   bsecs=bsecs, 
                                   rutDeudor=rutDeudor,
                                   apellidoDeudor=apellidoDeudor,
                                   idCliente=idCliente,
                                   nombreCliente=nombreCliente))
        return casosFound

    def insertBoletaDataExample(self):
        query = f'''
                    INSERT INTO {self.boletasTable} (IdBoleta, Numero, Fecha, Monto, Nota, Check, Mes, "RUT Beneficiario")
                    VALUES (1111, 1111, '{transformDateToSpanishBrief(date=datetime.now(), point=True)}' , 88888, 'Test Daniel', False, '{getFormattedMonthFromDate(datetime.now())}', '19.618.378-7')                              
                '''
        print(query)
        self.cursorBoleta.execute(query)
        self.connBoleta.commit()
        
    def insertBoletaData(self, boleta: Boleta):
        servicio: Servicio
        english: bool = LANGUAGE == 'ENG'
        for servicio in boleta.servicios:
            formattedDate: str = transformDateToSpanishBrief(date=boleta.fechaEmision, point=True, english=english)
            formattedMonth: str = getFormattedMonthFromDate(date=boleta.fechaEmision, english=english)
            query = f'''
                        INSERT INTO {self.boletasTable} (IdBoleta, Numero, Fecha, Monto, Nota, Check, Mes, "RUT Beneficiario", Codigo, "Valor Ref")
                        VALUES ({boleta.idMapsa}, {boleta.numBoleta}, '{formattedDate}', {servicio.monto}, '{servicio.nota if servicio.nota else " "}', False, '{formattedMonth}', '{boleta.rutBeneficiario}', '{servicio.codigo}', '{servicio.codigoHeader}')
                    '''
            print(query)
            self.cursorBoleta.execute(query)
            self.connBoleta.commit()
            
    def deleteBoletaData(self, numBoleta: int, idMapsa: int):
        self.cursorBoleta.execute(f'''
                                    DELETE FROM {self.boletasTable}
                                    WHERE IdBoleta = {idMapsa} AND Numero = {numBoleta}
                                  ''')
        self.connBoleta.commit()
                
    def getBoletaData(self, numBoleta: int) -> list:
        self.cursorBoleta.execute(f'''
                                    SELECT * FROM {self.boletasTable}
                                    WHERE Numero = {numBoleta} and Check = False
                                  ''')
        return self.cursorBoleta.fetchall()
        
    def clearAllBoletaData(self):
        self.cursorBoleta.execute(f'''
                                    DELETE FROM {self.boletasTable}
                                  ''')
        self.cursorBoleta.commit()
        
    def setBoletaAsPrinted(self, numBoleta: int, idMapsa: int):
        self.cursorBoleta.execute(f'''
                                    UPDATE {self.boletasTable}
                                    SET Check = True
                                    WHERE Idboleta = {idMapsa} AND Numero = {numBoleta}   
                                  ''')
        self.connBoleta.commit()
            
        