from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from wtforms import StringField, EmailField, PasswordField, validators
from flask_wtf import FlaskForm
from bd import conecta_no_banco_de_dados,cria_tabela_jogos

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessária para usar flash messages e cookies

@app.route('/validalogin', methods=['POST', 'GET'])
def login():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

    # Validar as credenciais
    bd = conecta_no_banco_de_dados()
    cursor = bd.cursor()
    cursor.execute("""
        SELECT *
        FROM contatos
        WHERE nome = %s AND email = %s AND senha = %s;
    """, (nome, email, senha))
    usuario = cursor.fetchone()
    cursor.close()
    bd.close()

    if usuario:
        # Login bem-sucedido
        session['usuario_id'] = usuario[0]
        session['usuario_nome'] = usuario[1]
        flash(f"{session['usuario_nome']} logado com sucesso!")
        return redirect(url_for('novo'))
    else:
        # Login inválido
        flash('Usuário não logado!')
        return redirect(url_for('pagina_login'))

class Jogo:
    def __init__(self, nome, categoria, console):
        self.nome = nome
        self.categoria = categoria
        self.console = console

jogo1 = Jogo('Tetris', 'Puzzle', 'Atari')
jogo2 = Jogo('God of War', 'Hack n Slash', 'PS2')
jogo3 = Jogo('Mortal Kombat', 'Luta', 'PS2')
lista = [jogo1, jogo2, jogo3]

@app.route('/inicio', methods=['GET']) 
def index():
    if 'usuario_nome' not in session or session['usuario_nome'] == None:
        return redirect(url_for('pagina_login'))
    usuario_nome = session.get('usuario_nome')  
    return render_template('lista.html', titulo='Jogos', jogos=lista, usuario=usuario_nome)

@app.route('/novo')
def novo():
    if 'usuario_nome' not in session or session['usuario_nome'] == None:
        return redirect(url_for('pagina_login'))
    return render_template('novo.html', titulo='Novo Jogo')

@app.route('/criar', methods=['POST'])
def criar():
    if 'usuario_nome' not in session or session['usuario_nome'] == None:
        return redirect(url_for('pagina_login'))
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console) ## acrescentar aqui logica para criacao da tabela e adicao de jogos a mesma.
    lista.append(jogo)
    bd =conecta_no_banco_de_dados()
            # A linha bd = conecta_no_banco_de_dados() tenta estabelecer uma conexão com o banco de dados usando a função conecta_no_banco_de_dados().
            # Essa função, é responsável por lidar com os detalhes da conexão.
    # bd = cria_tabela_jogos()
    cursor = bd.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM lista_de_jogos
        WHERE nome = %s AND categoria = %s AND console= %s;
    """, (nome,categoria,console))
    existe = cursor.fetchone()[0]
    bd = cria_tabela_jogos()
    cursor.close()
    bd.close()
    if existe > 0:
        flash('Email já cadastrado')
        return render_template('cadastro.html')
    else:
        try:
            bd = conecta_no_banco_de_dados()
            cursor = bd.cursor()
            sql = 'INSERT INTO lista_de_jogos (Nome, Categoria, console) VALUES (%s, %s, %s)'
            values = (nome, categoria, console)
            cursor.execute(sql, values)
            bd.commit()
            cursor.close()
            return redirect(url_for('index'))
        except mysql.connector.Error as e:
            return render_template('cadastro.html', error=str(e))

    

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

    # Validação
    if not nome:
        flash('O nome é obrigatório.')
        return render_template('cadastro.html')
    if not email:
        flash('O e-mail é obrigatório.')
        return render_template('cadastro.html')
    if not senha:
        flash('A senha é obrigatória.')
        return render_template('cadastro.html')

    bd = conecta_no_banco_de_dados()
    cursor = bd.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM contatos
        WHERE email = %s;
    """, (email,))
    existe = cursor.fetchone()[0]
    cursor.close()
    bd.close()

    if existe > 0:
        flash('Email já cadastrado')
        return render_template('cadastro.html')
    else:
        try:
            bd = conecta_no_banco_de_dados()
            cursor = bd.cursor()
            sql = 'INSERT INTO contatos (nome, email, senha) VALUES (%s, %s, %s)'
            values = (nome, email, senha)
            cursor.execute(sql, values)
            bd.commit()
            cursor.close()
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            return render_template('cadastro.html', error=str(e))

@app.route('/', methods=['GET', 'POST'])
def pagina_login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not nome or not email or not senha:
            flash("Todos os campos são obrigatórios.")
            return redirect(url_for('pagina_login'))

        bd = conecta_no_banco_de_dados()
        if bd is None:
            flash("Erro ao conectar ao banco de dados.")
            return redirect(url_for('pagina_login'))

        cursor = bd.cursor()
        try:
            cursor.execute("SELECT * FROM contatos WHERE nome=%s AND email=%s AND senha=%s", (nome, email, senha))
            user = cursor.fetchone()
            if user:
                session['usuario_id'] = user[0]
                session['usuario_nome'] = user[1]
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

@app.route('/logout')
def logout():
    session.pop('usuario_nome', None)
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('pagina_login'))

if __name__ == '__main__':
    db_conn = conecta_no_banco_de_dados()
    if db_conn:
        print("Conexão estabelecida com sucesso.")
        db_conn.close()
    app.run(debug=True)
