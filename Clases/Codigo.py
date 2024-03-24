class Codigo:
    def __init__(self, item: str, descripcion: str, montoReferencial: int):
        self.item = item
        self.descripcion = descripcion
        self.montoReferencial = montoReferencial
        
    def __repr__(self) -> str:
        return f'{self.item} | {self.descripcion} | {self.montoReferencial}'