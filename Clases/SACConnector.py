import openpyxl
from Clases.BoletaMatrixRow import BoletaMatrixRow
from Clases.Gestion import Gestion
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
from Clases.Codigo import Codigo
from datetime import datetime
from Utils.GlobalFunctions import *
from Clases.Caso import Caso
from Clases.Resumen import Resumen

class SACConnector:
    def __init__(self):
        pyodbc.pooling = False
        self.connBoleta: pyodbc.Connection = pyodbc.connect(SACBOLETASPATH)
        self.connData: pyodbc.Connection = pyodbc.connect(SACDATAPATH)
        self.connGestiones: pyodbc.Connection = pyodbc.connect(SACGESTIONESPATH)
        self.cursorBoleta: pyodbc.Cursor = self.connBoleta.cursor()
        self.cursorBoleta.fast_executemany = True
        self.cursorData: pyodbc.Cursor = self.connData.cursor()
        self.cursorData.fast_executemany = True
        self.cursorGestiones: pyodbc.Cursor = self.connGestiones.cursor()
        self.cursorGestiones.fast_executemany = True
        
        self.beneficiariosTable: str = 'Beneficiarios'
        self.clientesTable: str = 'Clientes'
        self.mapsaTable: str = 'Mapsa'
        self.boletasTable: str = 'Boletas'
        self.gastosTable: str = 'ITEM-Gastos'
        self.valoresTable: str = 'ITEM-Valores'
        self.destinatariosTable: str = 'Destinatarios'
        self.gestionesTable: str = 'Gestiones'
        
    def getDeudorData(self, idBoleta: int) -> Deudor | None:
        self.cursorData.execute(f'SELECT "Apellido Deudor", "Nombre Deudor", "Rut Deudor", Cliente FROM {self.mapsaTable} WHERE IdMapsa = {idBoleta}')
        apellidoDeudor, nombreDeudor, rutDeudor, idCliente = list(self.cursorData.fetchall())[0]
        return Deudor(apellidoDeudor=apellidoDeudor, nombreDeudor=nombreDeudor, rutDeudor=rutDeudor, idCliente=idCliente)
    
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
        query: str = f"SELECT * FROM {self.boletasTable} WHERE Numero = {numBoleta} AND Check = False AND Idboleta = {idMapsa}"
        self.cursorBoleta.execute(query)
        rutBeneficiario: str = ''
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
    
    def getDestinatarioByCliente(self, idCliente: int) -> Destinatario:
        self.cursorData.execute(f'''
                                    SELECT IdDestinatario, Nombre, Email, CC
                                    FROM {self.destinatariosTable}, {self.clientesTable}
                                    WHERE {self.destinatariosTable}.IdDestinatario = {self.clientesTable}.IdContacto AND IdCliente = {idCliente}
                                ''')
        ccString: str
        id, nombreDestinatario, correoDestinatario, ccString = self.cursorData.fetchall()[0]
        return Destinatario(id=id, nombreDestinatario=nombreDestinatario, correoDestinatario=correoDestinatario, cc=ccString.split(';') if ccString else [])
    
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
        self.cursorData.execute(f"""
                                    SELECT IdCliente, Cliente, "Facturar a"
                                    FROM {self.clientesTable}
                                    WHERE RUT <> ''
                                """)
        for data in self.cursorData.fetchall():
            idCliente, nombreCliente, factura = data
            clientesData.append(Cliente(idCliente=idCliente, nombreCliente=nombreCliente, factura=factura))
        return clientesData
    
    def getAllCodigos(self) -> list[Codigo]:
        codigos: list[Codigo] = []
        precios: dict = dict()
        self.cursorData.execute(f'''
                                    SELECT *
                                    FROM "{self.valoresTable}"
                                ''')
        for data in self.cursorData.fetchall():
            precio = int(data[0].replace('$','').replace('.','')) if data[0] else 0
            item = data[1]
            precios[item] = precio
        self.cursorData.execute(f'''
                                    SELECT ITEM
                                    FROM "{self.gastosTable}"
                                ''')
        for data in self.cursorData.fetchall():
            item = data[0][0:4]
            descripcion = data[0][5::]
            valor = precios.get(item, 0)
            codigos.append(Codigo(item=item, descripcion=descripcion, montoReferencial=valor))
        return codigos
    
    def getAllBeneficiarios(self) -> list[Beneficiario]:
        beneficiariosData: list[Beneficiario] = []
        self.cursorData.execute(f'''
                                    SELECT "RUT Beneficiario", "Nombre o Razón Social"
                                    FROM {self.beneficiariosTable}
                                    ORDER BY `Nombre o Razón Social` ASC;
                                ''')
        for data in self.cursorData.fetchall():
            rutBeneficiario, nombreBeneficiario = data
            beneficiariosData.append(Beneficiario(rutBeneficiario=rutBeneficiario, nombreBeneficiario=nombreBeneficiario))
        return beneficiariosData
    
    def getAllDestinatarios(self) -> list[Destinatario]:
        destinatariosData: list[Destinatario] = []
        self.cursorData.execute(f'''
                                    SELECT IdDestinatario, Nombre, Email, CC
                                    FROM {self.destinatariosTable}
                                ''')
        for data in self.cursorData.fetchall():
            ccString: str
            id, nombreDestinatario, correoDestinatario, ccString = data
            if ccString:
                cc = ccString.split(';')
            else:
                cc = []
            destinatariosData.append(Destinatario(id=id, nombreDestinatario=nombreDestinatario, correoDestinatario=correoDestinatario, cc=cc))
        return destinatariosData 
    
    def getPossibleMapsaCasos(self, rutDeudor: str = '', apellidoDeudor: str = '', nombreDeudor: str = '', idCliente: int = None, active: bool = True) -> list[Caso]:
        casosFound : list[Caso] = []
        query: str = f'''
                        SELECT IdMapsa, Estado, Asignado, Bsecs, "Apellido Deudor", "Nombre Deudor", "RUT Deudor", Mapsa.Cliente, Clientes.Cliente, "Facturar a", Num, Folio
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
        if nombreDeudor:
            query += f"""AND "Nombre Deudor" LIKE '{nombreDeudor}%'""" 

        if not active:
            query = query.replace("Estado LIKE '%Activo%'\n", "1")
        
        self.cursorData.execute(query)
        for data in self.cursorData.fetchall():
            idMapsa, nombreEstado, fechaAsignado, bsecs, apellidoDeudor, nombreDeudor, rutDeudor, idCliente, nombreCliente, factura, nOperacion, folio = data
            casosFound.append(Caso(idMapsa=idMapsa, 
                                   nombreEstado=nombreEstado, 
                                   fechaAsignado=fechaAsignado, 
                                   bsecs=bsecs, 
                                   rutDeudor=rutDeudor,
                                   nombreDeudor=nombreDeudor,
                                   apellidoDeudor=apellidoDeudor,
                                   idCliente=idCliente,
                                   nombreCliente=nombreCliente,
                                   factura=factura,
                                   nOperacion=nOperacion,
                                   folio=folio))
        return casosFound

    def insertBoletaDataExample(self):
        query = f'''
                    INSERT INTO {self.boletasTable} (IdBoleta, Numero, Fecha, Monto, Nota, Check, Mes, "RUT Beneficiario")
                    VALUES (1111, 1111, '{transformDateToSpanishBrief(date=datetime.now(), point=True)}' , 88888, 'Test Daniel', False, '{getFormattedMonthFromDate(datetime.now())}', '19.618.378-7')                              
                '''
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
            self.cursorBoleta.execute(query)
            self.connBoleta.commit()
            
    def deleteBoletaData(self, numBoleta: int, idMapsa: int):
        self.cursorBoleta.execute(f'''
                                    DELETE FROM {self.boletasTable}
                                    WHERE IdBoleta = {idMapsa} AND Numero = {numBoleta} AND Check = False
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
    
    def getCCByDestinatario(self, nombreDestinatario: str) -> list[str]:
        query = f"""
                    SELECT CC FROM {self.destinatariosTable}
                    WHERE Nombre LIKE '%{nombreDestinatario}%'
                """
        self.cursorData.execute(query)
        rawData = self.cursorData.fetchall()
        if not rawData:
            return []
        result: str = rawData[0][0]
        return result.split(';') if result else []
    
    def getBoletaServicios(self, numBoleta: int, idMapsa: int) -> list:
        self.cursorBoleta.execute(f"""
                                    SELECT Codigo, Monto
                                    FROM {self.boletasTable}
                                    WHERE Numero = {numBoleta} AND IdBoleta = {idMapsa} AND Check = False
                                  """)
        result: list = self.cursorBoleta.fetchall()
        return result
    
    def setMapsaCasoState(self, idMapsa: int, newState: str):
        timestamp: str = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        query: str = f'''
                    UPDATE {self.mapsaTable}
                    SET Estado = '{newState}', FechaModificacion = '{timestamp}'
                    WHERE IdMapsa = {idMapsa}
                '''
        self.cursorData.execute(query)
        self.connData.commit()

    def addGestion(self, gestion: Gestion):
        query: str = f'''
                        INSERT INTO {self.gestionesTable} (IdJuicio, Fecha, Gestion, Nota, Usuario)
                        VALUES ({gestion.idJuicio}, '{gestion.fecha}', '{gestion.gestion}', '{gestion.nota}', '{gestion.user}')
                     '''
        self.cursorGestiones.execute(query)
        self.connGestiones.commit()
        
    def getLastGestionControl(self, idMapsa: int) -> datetime | None:
        query: str = f'''
                        SELECT TOP 1 Fecha
                        FROM {self.gestionesTable}
                        WHERE Idjuicio = {idMapsa}
                        ORDER BY Fecha DESC
                    '''
        self.cursorGestiones.execute(query)
        data = self.cursorGestiones.fetchall()
        if data:
            return data[0][0]
        else:
            return None
        
    def getBoletaMatrixRows(self, numBoleta: int) -> list[BoletaMatrixRow]:
        query = f'''
                    SELECT IdBoleta, Numero, Fecha, Monto, "RUT Beneficiario", Codigo
                    FROM {self.boletasTable}
                    WHERE Numero = {numBoleta}
                '''
        self.cursorBoleta.execute(query)
        dataServicios = self.cursorBoleta.fetchall()
        if not dataServicios:
            return []
        idMapsa = int(dataServicios[0][0])
        nBoleta = int(dataServicios[0][1])
        fechaPago = dataServicios[0][2].strftime("%d-%m-%Y")
        rutBeneficiario = dataServicios[0][4]
        nombreBeneficiario = ''
        beneficiario : Beneficiario
        for beneficiario in self.getAllBeneficiarios():
            if beneficiario.rutBeneficiario == rutBeneficiario:
                nombreBeneficiario = beneficiario.nombreBeneficiario
        query = f'''
                    SELECT m.Num, m.Folio, m."Apellido Deudor", m."Nombre Deudor"
                    FROM {self.mapsaTable} as m
                    WHERE IdMapsa = {idMapsa}
                '''
        self.cursorData.execute(query)
        dataCaso = self.cursorData.fetchall()[0]
        nOperacion = str(dataCaso[0]) if dataCaso[0] else '-'
        nFolio = str(dataCaso[1]) if dataCaso[1] else '-'
        apellidoDeudor = dataCaso[2]
        nombreDeudor = dataCaso[3]
        rows: list[BoletaMatrixRow] = []
        for dataServicio in dataServicios:
            codigo: str = dataServicio[5]
            item: str = codigo.split(' ')[0]
            nombreServicio: str = ' '.join(codigo.split(' ')[1::])
            monto: int = int(dataServicio[3])
            row: BoletaMatrixRow = BoletaMatrixRow(nombreDeudor=apellidoDeudor + ' ' + nombreDeudor,
                                                   nOperacion=nOperacion,
                                                   nFolio=nFolio,
                                                   item=item,
                                                   nombreServicio=nombreServicio,
                                                   rutPrestador=rutBeneficiario,
                                                   nombrePrestador=nombreBeneficiario,
                                                   monto=monto,
                                                   nBoleta=nBoleta,
                                                   fechaPago=fechaPago)
            rows.append(row)
        return rows
            
    def getClienteMatrixRows(self, nombreDestinatario: str, nombreCliente: str) -> list[BoletaMatrixRow]:
        rows: list[BoletaMatrixRow] = []
        for dirName in os.listdir(path=f'{DELIVEREDDATAPATH}/{nombreDestinatario}'):
            if dirName[0] == 'R' or dirName == 'Documento.pdf':
                 continue
            numBoleta, idCaso = dirName.split('_')
            numBoleta = int(numBoleta)
            idCaso = int(idCaso)
            filename = f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{dirName}/Data_{numBoleta}.txt'
            if not os.path.exists(filename):
                continue
            with open(file=filename) as file:
                fileNombreCliente = file.readline().strip().split(';')[5]
                if nombreCliente != fileNombreCliente:
                    continue
            rows.extend(self.getBoletaMatrixRows(numBoleta=numBoleta))
        return rows
    
    def getRendicionNumber(self, nombreDestinatario: str, nombreCliente: str) -> int:
        if not os.path.exists(GENERATEDREPORTSPATH):
            return 1
        if not os.listdir(GENERATEDREPORTSPATH):
            return 1
        dirNames = list(filter(lambda x:x[0] != 'S', os.listdir(GENERATEDREPORTSPATH)))
        dates: list[datetime] = [datetime.strptime(dirName, '%Y-%m-%d') for dirName in os.listdir(GENERATEDREPORTSPATH)]
        dates.sort(reverse=True)
        date: datetime
        for date in dates:
            dirName = str(date).split(' ')[0]
            for destinatarioName in os.listdir(f'{GENERATEDREPORTSPATH}/{dirName}'):
                if destinatarioName == nombreDestinatario:
                    maxNumber: int = 0
                    for filename in os.listdir(f'{GENERATEDREPORTSPATH}/{dirName}/{nombreDestinatario}'):
                        if nombreCliente in filename:
                            number = int(filename.replace('.xlsx', '')[-1])
                            if number > maxNumber:
                                maxNumber = number
                    return maxNumber + 1
        return 1
    
    def getCodigoMontoReferencial(self, codigo: str) -> int:
        self.cursorData.execute(f'''
                                    SELECT "$    REFERENCIA"
                                    FROM "ITEM-VALORES"
                                    WHERE ITEM = {codigo}
                                ''')
        result = self.cursorData.fetchall()[0][0]
        return int(result)
    
    def getBoletasFromCaso(self, idCaso: int) -> list[int]:
        self.cursorBoleta.execute(f'''
                                    SELECT Numero
                                    FROM {self.boletasTable}
                                    WHERE Idboleta = {idCaso} AND Check = False
                                  ''')
        data = [elem[0] for elem in self.cursorBoleta.fetchall()]
        return data
            
    def getClienteFromCasoId(self, idMapsa: int) -> Cliente | None:
        self.cursorData.execute(f'''
                                    SELECT m.Cliente, c.Cliente
                                    FROM {self.mapsaTable} AS m
                                    INNER JOIN {self.clientesTable} AS c
                                    ON m.Cliente = c.IdCliente
                                    WHERE m.IdMapsa = {idMapsa} 
                                ''')
        data = self.cursorData.fetchall()
        if data:
            idCliente: int = data[0][0]
            nombreCliente: str = data[0][1]
            return Cliente(idCliente=idCliente, nombreCliente=nombreCliente)
        else:
            return None
        
    def getRecurrentGestiones(self, delay: timedelta, idsCasos: list[int]) -> list[Gestion]:
        if not idsCasos:
            return []
        query: str = f'''
                        SELECT "RUT Deudor", "Nombre Deudor", "Apellido Deudor"
                        FROM {self.mapsaTable}
                        WHERE IdMapsa IN ({','.join([str(x) for x in idsCasos])})
                    '''
        self.cursorData.execute(query)
        casosData = self.cursorData.fetchall()
        query: str = f'''
                        SELECT Idjuicio, Control, Gestion, Usuario
                        FROM {self.gestionesTable}
                        WHERE Idjuicio IN ({','.join([str(x) for x in idsCasos])})
                    '''
        self.cursorGestiones.execute(query)
        data = self.cursorGestiones.fetchall()
        gestiones: list[Gestion] = []
        for gestionData, deudorData in zip(data, casosData):
            rutDeudor, nombreDeudor, apellidoDeudor = deudorData
            idJuicio: int = int(gestionData[0])
            fechaGestion: datetime = gestionData[1]
            gestionTipo: str = gestionData[2]
            username: str = gestionData[3]
            if (datetime.now() - fechaGestion).days < delay and idJuicio not in [int(gestion.idJuicio) for gestion in gestiones]:
                gestiones.append(Gestion(idJuicio=idJuicio, timestamp=fechaGestion, tipo=gestionTipo, user=username, rutDeudor=rutDeudor, nombreDeudor=nombreDeudor + ' ' + apellidoDeudor)) 
        return gestiones

    def setAllCasos(self, newState: str):
        self.cursorData.execute(f"UPDATE {self.mapsaTable} SET Estado = '{newState}'")
        self.connData.commit()

    def deleteAllGestiones(self):
        self.cursorGestiones.execute(f"""DELETE FROM {self.gestionesTable}""")
        self.connGestiones.commit()
        self.cursorBoleta.close()
        self.connBoleta.close()

        