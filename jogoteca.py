from flask import Flask, render_template, request, redirect, url_for, flash, session,make_response
import mysql.connector
from wtforms import StringField, EmailField, PasswordField, validators
from flask_wtf import FlaskForm
import reportlab
from xlsxwriter import Workbook
from reportlab.lib.pagesizes import letter
from io import BytesIO
from bd import conecta_no_banco_de_dados,cria_tabela_jogos

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  

@app.route('/validalogin', methods=['POST', 'GET'])
def login():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

   
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
    if 'usuario_nome' not in session or session['usuario_nome'] is None:
        return redirect(url_for('pagina_login'))

    bd = conecta_no_banco_de_dados()
    cursor = bd.cursor()
    cursor.execute("SELECT nome, categoria, console FROM lista_de_jogos")
    jogos = cursor.fetchall()
    cursor.close()
    bd.close()

    usuario_nome = session.get('usuario_nome')  
    return render_template('lista.html', titulo='Jogos', jogos=jogos, usuario=usuario_nome)


@app.route('/novo')
def novo():
    if 'usuario_nome' not in session or session['usuario_nome'] == None:
        return redirect(url_for('pagina_login'))
    return render_template('novo.html', titulo='Novo Jogo')

@app.route('/criar', methods=['POST'])
def criar():
    if 'usuario_nome' not in session or session['usuario_nome'] is None:
        return redirect(url_for('pagina_login'))

    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']

    bd = conecta_no_banco_de_dados()
    cursor = bd.cursor()

    # Criar a tabela de jogos se não existir
    cria_tabela_jogos()

    # Verificar se o jogo já existe na lista de jogos
    cursor.execute("""
        SELECT COUNT(*)
        FROM lista_de_jogos
        WHERE nome = %s AND categoria = %s AND console = %s;
    """, (nome, categoria, console))
    existe = cursor.fetchone()[0]

    if existe > 0:
        flash('Jogo já cadastrado')
        cursor.close()
        bd.close()
        return render_template('novo.html', titulo='Novo Jogo')

    try:
        sql = 'INSERT INTO lista_de_jogos (nome, categoria, console) VALUES (%s, %s, %s)'
        values = (nome, categoria, console)
        cursor.execute(sql, values)
        bd.commit()
        flash('Jogo adicionado com sucesso!')
    except mysql.connector.Error as e:
        flash('Erro ao adicionar o jogo: ' + str(e))
    finally:
        cursor.close()
        bd.close()

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

@app.route('/excluir_usuario/<nome>', methods=['GET', 'POST'])
def excluir_usuario(nome):
    nome = session.get['usuario_nome']
    print(nome)
    # Validar o ID
    if  nome.isdigit():
        return render_template('login.html', error='ID inválido')
    # Executando a exclusão
    try:
        bd =conecta_no_banco_de_dados()
            # A linha bd = conecta_no_banco_de_dados() tenta estabelecer uma conexão com o banco de dados usando a função conecta_no_banco_de_dados().
            # Essa função, é responsável por lidar com os detalhes da conexão.
            
        cursor = bd.cursor()
        cursor.execute("""
            DELETE FROM contatos
            WHERE nome = %s;
        """, (nome,))
        cursor.close()
        bd.commit()

        return redirect(url_for('login'))
    except bd.connector.Error as e:
        return render_template('excluir-usuario.html', error=str(e))



@app.route('/relatorio_excel')
def gerar_relatorio():
    # Obter o ID do usuário da sessão
    # usuario_id = session.get('usuario_id')
    nome = session.get['usuario_nome']
    # Conectar ao banco de dados
    bd = conecta_no_banco_de_dados()
    cursor = bd.cursor()

    # Executar consulta SQL
    cursor.execute("""
        SELECT ct.*
        FROM contatos AS ct
        INNER JOIN nome AS uc ON uc.contato_id = ct.id_contato
        WHERE uc.usuario_id = %s order by ct.id_contato
    """, (nome,),)

    data = []
    for row in cursor.fetchall():
        data.append(row)

    # Criar um objeto de planilha do Excel em memória
    output = io.BytesIO()
    workbook = Workbook(output)
    worksheet = workbook.add_worksheet()

    # Definir o cabeçalho da planilha
    worksheet.write('A1', 'ID')
    worksheet.write('B1', 'Nome')
    worksheet.write('C1', 'Email')
    worksheet.write('D1', 'Mensagem')
    
    # Escrever os dados da tabela na planilha
    for i, row in enumerate(data):
        worksheet.write(i + 1, 0, row[0])
        worksheet.write(i + 1, 1, row[1])
        worksheet.write(i + 1, 2, row[2])
        worksheet.write(i + 1, 3, row[3])
      

    # Salvar a planilha na memória
    workbook.close()
    output.seek(0)

    # Criar a resposta HTTP com os cabeçalhos corretos
    response = make_response(output.read())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_contatos.xlsx'

    return response
@app.route('/relatorio_pdf')
def gerar_relatorio_pdf():
    # Obter o ID do usuário da sessão
    usuario_id = session.get('usuario_id')

    # Conectar ao banco de dados
    bd = conecta_no_banco_de_dados()
    cursor = bd.cursor()

    # Executar consulta SQL
    cursor.execute("""
    SELECT ct.*
    FROM contatos AS ct
    INNER JOIN usuario_contato AS uc ON uc.contato_id = ct.id_contato
    WHERE uc.usuario_id = %s order by ct.id_contato
    """, (usuario_id,),)

    # Obter os dados da consulta
    data = cursor.fetchall()

    # Criar um PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setTitle('Relatório de Contatos')

    # Definir o cabeçalho do relatório
    c.setFont('Times-Roman', 12)
    c.drawString(25, 750, 'Relatório de Contatos')

    # Definir as colunas do relatório
    c.setFont('Times-Roman', 10)
    c.drawString(25, 725, 'ID')
    c.drawString(100, 725, 'Nome')
    c.drawString(200, 725, 'Email')
    c.drawString(300, 725, 'Mensagem')

    # Escrever os dados da tabela no relatório
    for i, row in enumerate(data):
        y = 700 - i * 25
        c.setFont('Times-Roman', 8)
        c.drawString(25, y, str(row[0]))
        c.drawString(100, y, str(row[1]))
        c.drawString(200, y, str(row[2]))
        c.drawString(300, y, str(row[3]))

    # Salvar o conteúdo do PDF no buffer
     # Salvar o conteúdo do PDF no buffer
    c.save()

    # Obter o conteúdo do buffer como uma string
    pdf_content = buffer.getvalue()

     
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio.pdf'

    # Retornar a resposta para iniciar o download
    return response

@app.route('/logout')
def logout():
    session.pop('usuario_nome', None)
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('pagina_login'))

if __name__ == '__main__':
    db_conn = conecta_no_banco_de_dados()
    if db_conn:
        cria_tabela_jogos()
        
        db_conn.close()
    app.run(debug=True)

