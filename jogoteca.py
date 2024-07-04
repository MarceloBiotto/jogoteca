from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessária para usar flash messages e cookies

def conecta_no_banco_de_dados():
    try:
       
        cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
        )
        cursor = cnx.cursor()

        # Verifica se o banco de dados 'jogoteca' já existe
        cursor.execute("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = 'jogoteca'")
        result = cursor.fetchone()

        if not result:
            # Se o banco de dados não existe, crie-o
            print('Banco de dados jogoteca não encontrado. Criando novo banco de dados...')
            cria_banco_de_dados_e_tabelas(cnx)
        else:
            print('O banco de dados jogoteca existe e está pronto para uso.')

        cursor.close()
        cnx.close()

        # Conecte-se ao banco de dados específico 'jogoteca'
        bd = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='jogoteca'
        )
        return bd

    except mysql.connector.Error as err:
        print("Erro de conexão com o banco de dados:", err)
        raise

def cria_banco_de_dados_e_tabelas(cnx):
    try:
        cursor = cnx.cursor()
        # Cria o banco de dados 'jogoteca'
        cursor.execute('CREATE DATABASE jogoteca;')
        cnx.commit()

        # Seleciona o banco de dados recém-criado
        cnx.database = 'jogoteca'
        
        # Cria a tabela 'contatos'
        cursor.execute('''
            CREATE TABLE contatos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                senha VARCHAR(255) NOT NULL
            );
        ''')
        cnx.commit()

        # Insere um exemplo de contato
        nome = "ROOT"
        email = "lee.am@live.com"
        senha = "12345"
        sql = "INSERT INTO contatos (nome, email, senha) VALUES (%s, %s, %s)"
        valores = (nome, email, senha)
        cursor.execute(sql, valores)
        cnx.commit()

        print('Banco de dados e tabelas criados com sucesso.')

    except mysql.connector.Error as err:
        print("Erro ao criar banco de dados ou tabelas:", err)
        raise
    finally:
        cursor.close()

class Jogo:
    def __init__(self, nome, categoria, console):
        self.nome = nome
        self.categoria = categoria
        self.console = console

jogo1 = Jogo('Tetris', 'Puzzle', 'Atari')
jogo2 = Jogo('God of War', 'Hack n Slash', 'PS2')
jogo3 = Jogo('Mortal Kombat', 'Luta', 'PS2')
lista = [jogo1, jogo2, jogo3]

@app.route('/inicio')
def index():
    return render_template('lista.html', titulo='Jogos', jogos=lista)

@app.route('/novo')
def novo():
    return render_template('novo.html', titulo='Novo Jogo')

@app.route('/criar', methods=['POST'])
def criar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console)
    lista.append(jogo)
    return redirect(url_for('index'))  

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if not nome or not email or not senha:
            flash("Todos os campos são obrigatórios.")
            return redirect(url_for('cadastrar'))

        bd = conecta_no_banco_de_dados()
        if bd is None:
            flash("Erro ao conectar ao banco de dados.")
            return redirect(url_for('cadastrar'))

        cursor = bd.cursor()
        try:
            cursor.execute("INSERT INTO contatos (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
            bd.commit()
            flash("Usuário cadastrado com sucesso.")
            return redirect(url_for('pagina_login'))
        except mysql.connector.Error as err:
            flash("Erro ao cadastrar usuário: {}".format(err))
            bd.rollback()
        finally:
            cursor.close()
            bd.close()

    return render_template('cadastro.html')

@app.route('/', methods=['GET', 'POST'])
def pagina_login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not email or not senha:
            flash("Todos os campos são obrigatórios.")
            return redirect(url_for('pagina_login'))

        bd = conecta_no_banco_de_dados()
        if bd is None:
            flash("Erro ao conectar ao banco de dados.")
            return redirect(url_for('pagina_login'))

        cursor = bd.cursor()
        try:
            cursor.execute("SELECT * FROM contatos WHERE email=%s AND senha=%s", (email, senha))
            user = cursor.fetchone()
            if user:
                flash("Login realizado com sucesso.")
                return redirect(url_for('index'))  
            else:
                flash("Usuário ou senha incorretos.")
        except mysql.connector.Error as err:
            flash("Erro ao realizar login: {}".format(err))
        finally:
            cursor.close()
            bd.close()

    return render_template('login.html')

if __name__ == '__main__':
    db_conn = conecta_no_banco_de_dados()
    if db_conn:
        print("Conexão estabelecida com sucesso.")
        db_conn.close()
    app.run(debug=True)
