class Beneficiario:
    def __init__(self, rutBeneficiario : str, nombreBeneficiario: str):
        self.rutBeneficiario = rutBeneficiario
        self.nombreBeneficiario = nombreBeneficiario
        
    def __repr__(self):
        return str(self.__dict__)