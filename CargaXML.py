import pyodbc

# Configuración de conexión a la base de datos
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=mssql-180519-0.cloudclusters.net,10034;'
        'DATABASE=Tarea3;'
        'UID=Admin;'
        'PWD=Db12345678;'
        'Encrypt=no;'  # Desactivar SSL solo para pruebas
        'TrustServerCertificate=yes;'  # Confiar en el certificado del servidor
    )
    return conn


# Crear un cursor para ejecutar consultas
conn = get_db_connection()
cursor = conn.cursor()

# Leer el archivo XML
try:
    n =1
    if (n==0):
        with open('/Users/danielmendez/Desktop/Tarea-BD-3-y-4/CatalogosFinal.xml', 'r', encoding='utf-8') as file:
            xml_data = file.read()

        # Ejecutar el procedimiento almacenado pasando el XML como parámetro
        cursor.execute("EXEC dbo.ProcesarXML @XMLDoc=?", (xml_data,))
    else:

        with open('/Users/danielmendez/Desktop/Tarea-BD-3-y-4/OperacionesFinal.xml', 'r', encoding='utf-8') as file:
            xml_data = file.read()

        # Ejecutar el procedimiento almacenado pasando el XML como parámetro
        cursor.execute("EXEC dbo.ProcesarSegmentosXML @XMLDoc=?", (xml_data,))

        # Si el procedimiento no maneja la transacción, puedes descomentar esto:
        # conn.commit()

    print("Procedimiento ejecutado correctamente.")
    cursor.commit()

except Exception as e:
    print(f"Ocurrió un error: {e}")
finally:
    # Cerrar la conexión
    cursor.close()
    conn.close()
