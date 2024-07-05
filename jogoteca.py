from flask import Flask, render_template, request, redirect, url_for, flash,session
import mysql.connector
from wtforms import StringField, EmailField, PasswordField, validators
from flask_wtf import FlaskForm
from bd import conecta_no_banco_de_dados




app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessária para usar flash messages e cookies


@app.route('/validalogin', methods=['POST', 'GET'])
def login():
  
  email = request.form.get('email')
  senha = request.form.get('senha')

  # Validar as credenciais
  bd =conecta_no_banco_de_dados()
            # A linha bd = conecta_no_banco_de_dados() tenta estabelecer uma conexão com o banco de dados usando a função conecta_no_banco_de_dados().
            # Essa função, é responsável por lidar com os detalhes da conexão.
            
  cursor = bd.cursor()
  cursor.execute("""
            SELECT *
            FROM contatos
            WHERE email = %s AND senha = %s;
        """, (email, senha,))
  usuario = cursor.fetchone()
  cursor.close()
  bd.close()

  if usuario:
  # Login bem-sucedido
   session['usuario_id'] = usuario[0]
   return redirect(url_for('inicio'))
  else:
    # Login inválido
    
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

@app.route('/inicio', methods=['GET',])
def index():
    nome = request.form.get('nome')
    return render_template('lista.html', titulo='Jogos', jogos=lista, usuario = nome) ## aqui nao funciona ainda na proxima feature sera implementado o nome do usuario logado de maneira correta

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
    # Abre uma conexão com o banco de dados MySQL usando as credenciais especificadas.
    bd =conecta_no_banco_de_dados()
                # A linha bd = conecta_no_banco_de_dados() tenta estabelecer uma conexão com o banco de dados usando a função conecta_no_banco_de_dados().
                # Essa função, é responsável por lidar com os detalhes da conexão.
                
    cursor = bd.cursor()
            
    # Executa uma consulta SQL para verificar se já existe um usuário com o email informado.
    cursor.execute("""
        SELECT COUNT(*)
        FROM contatos
        WHERE email = %s;
        """, (email,))
            
    # Obtém o resultado da consulta (o número de usuários encontrados).
    existe = cursor.fetchone()[0]
            
    # Fecha o cursor e a conexão com o banco de dados.
    cursor.close()
    bd.close()
    # Se a consulta anterior retornou um valor maior que zero (usuário já existe), renderiza o template 'cadastro.html' novamente, passando uma mensagem de erro.
    if existe > 0:
        flash('Email já cadastrado')
        return render_template('cadastro.html')
    else:
        try:
        # Reabre a conexão com o banco.
            bd =conecta_no_banco_de_dados()
                    # A linha bd = conecta_no_banco_de_dados() tenta estabelecer uma conexão com o banco de dados usando a função conecta_no_banco_de_dados().
                    # Essa função, é responsável por lidar com os detalhes da conexão.
                    
            cursor = bd.cursor()
                        
            # Prepara a consulta SQL de inserção.
            sql = 'INSERT INTO contatos (nome, email, senha) VALUES (%s, %s, %s)'
            values = (nome, email, senha)

            # Executa a consulta com os valores obtidos do formulário.
            cursor.execute(sql, list(values))
            # Fecha o cursor e confirma a transação (commit).
            cursor.close()
            bd.commit()

            # Redireciona para a página inicial.
            return redirect(url_for('login'))
            # Se ocorrer um erro de banco de dados, renderiza o template 'cadastro.html' novamente, passando a mensagem de erro SQL.
        except bd.connector.Error as e:   
                return render_template('cadastro', error=str(e)) 
            
          # Se o usuário não existe, tenta inserir o novo usuário no banco de dados:   
    
  

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
