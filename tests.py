from SACConnector import SACConnector

conn = SACConnector()
print(conn.getBeneficiarioData(6109))
print(conn.getDestinatarioData(6109))
print(conn.getServicios(6109))