import mysql.connector

def conecta_no_banco_de_dados():
    cnx = mysql.connector.connect(host='127.0.0.1',user='root',password='')

    # Executar a instrução SQL para verificar se o banco de dados existe
    cursor = cnx.cursor()
    cursor.execute('SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = "jogoteca";')

    # Obter o número de resultados
    num_results = cursor.fetchone()[0]

    # Fechar a conexão com o banco de dados
    cnx.close()

    # Se o número de resultados for maior que zero, o banco de dados existe
    if num_results > 0:
        print('O banco de dados jogoteca existe e esta pronto para uso.')
    else:
        # Conectar-se ao servidor MySQL para criar o banco de dados
        cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password=''
        )

        # Criar o banco de dados aula06
        cursor = cnx.cursor()
        cursor.execute('CREATE DATABASE jogoteca;')
        cnx.commit()

    # Conectar-se ao banco de dados jogoteca recém-criado
        cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='jogoteca'  # Especificar o banco de dados
        )
        
    try:
        bd = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='jogoteca'
        )
    except mysql.connector.Error as err:
        print("Erro de conexão com o banco de dados:", err)
        raise
    
    return bd