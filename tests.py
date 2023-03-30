from Clases.SACConnector import SACConnector

conn = SACConnector()

conn.cursorData.execute('''
                            SELECT *
                            FROM Mapsa
                            WHERE IdMapsa = 4096
                        ''')

print(conn.cursorData.fetchall())