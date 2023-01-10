import pyodbc

if __name__ == '__main__':
    conn = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\daguilera\Desktop\SAC\SAC Boletas.accdb;")
    cursor = conn.cursor()
    # print(conn)
    # print(cursor)

    # for row in cursor.tables():
    #     print(row.table_name)
    cursor.execute('select * from Tabla_nueva_de_boletas')
   
    for row in cursor.fetchall():
        print (row)
        break