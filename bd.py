import mysql.connector
from mysql.connector import Error

def conecta_no_banco_de_dados():
    try:
        cnx = mysql.connector.connect(host='127.0.0.1', user='root', password='')
        cursor = cnx.cursor()

        cursor.execute('SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = "jogoteca";')
        num_results = cursor.fetchone()[0]

        if num_results == 0:
            print('Banco de dados jogoteca não encontrado. Criando novo banco de dados...')
            cria_banco_de_dados_e_tabelas(cnx)
        else:
            print('O banco de dados jogoteca existe e está pronto para uso.')

        cursor.close()
        cnx.close()

        bd = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='jogoteca'
        )
        return bd

    except Error as err:
        print("Erro de conexão com o banco de dados:", err)
        raise

def cria_banco_de_dados_e_tabelas(cnx):
    try:
        cursor = cnx.cursor()
        cursor.execute('CREATE DATABASE jogoteca;')
        cnx.commit()

        cnx.database = 'jogoteca'
        
        cursor.execute('''
            CREATE TABLE contatos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                senha VARCHAR(255) NOT NULL
            );
        ''')
        cnx.commit()

        nome = "ROOT"
        email = "lee.am@live.com"
        senha = "12345"
        sql = "INSERT INTO contatos (nome, email, senha) VALUES (%s, %s, %s)"
        valores = (nome, email, senha)
        cursor.execute(sql, valores)
        cnx.commit()

        print('Banco de dados e tabelas criados com sucesso.')

    except Error as err:
        print("Erro ao criar banco de dados ou tabelas:", err)
        raise
    finally:
        cursor.close()

if __name__ == '__main__':
    db_conn = conecta_no_banco_de_dados()
    if db_conn:
        print("Conexão estabelecida com sucesso.")
        db_conn.close()
