from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessária para usar flash messages e cookies

def conecta_no_banco_de_dados():
    try:
        return mysql.connector.connect(
            host='127.0.0.1', 
            user='root', 
            password='', 
            database='jogoteca', 
            charset='utf8mb4'
        )
    except mysql.connector.Error as err:
        print("Erro ao conectar ao banco de dados:", err)
        return None

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
def ola():
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
    return redirect(url_for('ola'))

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

@app.route('/login', methods=['GET', 'POST'])
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
                return redirect(url_for('ola'))
            else:
                flash("Usuário ou senha incorretos.")
        except mysql.connector.Error as err:
            flash("Erro ao realizar login: {}".format(err))
        finally:
            cursor.close()
            bd.close()

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
