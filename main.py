import pyodbc

original_driver = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\User\Desktop\SAC\SAC Boletas.accdb"

if __name__ == '__main__':
    conn = pyodbc.connect(r"Driver={CData ODBC Driver for Microsoft Access};DBQ=C:\Users\User\Desktop\SAC\SAC Boletas.accdb")
    cursor = conn.cursor()
    print(conn)
    print(cursor)
    print(cursor.tables())
    for row in cursor.tables():
        print(row.table_name)
    cursor.execute('select * from Tabla_nueva_de_boletas')
   
    for row in cursor.fetchall():
       print (row)
       break

    msa_drivers = [x for x in pyodbc.drivers() if 'ACCESS' in x.upper()]

    print(msa_drivers)