class BoletaMatrixRow:
    def __init__(self, nombreDeudor: str, nOperacion: str, nFolio: str, item: str, nombreServicio: str, rutPrestador: str, nombrePrestador: str, monto: int, nBoleta: int, fechaPago: str):
        self.nombreDeudor = nombreDeudor
        self.nOperacion = nOperacion
        self.nFolio = nFolio
        self.item = item
        self.nombreServicio = nombreServicio
        self.rutPrestador = rutPrestador
        self.nombrePrestador = nombrePrestador
        self.monto = monto
        self.nBoleta = nBoleta
        self.fechaPago = fechaPago
        
    def __str__(self):
        return f'{self.nombreDeudor}|{self.nOperacion}|{self.nFolio}|{self.item}|{self.nombreServicio}|{self.rutPrestador}|{self.nombrePrestador}|{self.monto}|{self.nBoleta}|{self.fechaPago}\n'
    
    def __repr__(self):
        return self.__str__()