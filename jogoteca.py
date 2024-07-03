from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, validators
from typing import NotRequired
from bd import conecta_no_banco_de_dados

app = Flask(__name__)

class Jogo:
    def __init__(self, nome, categoria, console):
        self.nome = nome
        self.categoria = categoria
        self.console = console

@app.route('/inicio')  ## rota para acessa a lista de jogos do usuario acessado
def ola():
    jogo1 = Jogo('Tetris', 'Puzzle', 'Atari')
    jogo2 = Jogo('God of War', 'Hack n Slash', 'PS2')
    jogo3 = Jogo('Mortal Kombat', 'Luta', 'PS2')
    lista = [jogo1, jogo2, jogo3]
    return render_template('lista.html', titulo='Jogos', jogos=lista)




class FormularioCadastro(FlaskForm):
    nome = StringField('Nome:', validators=[validators.DataRequired()])
    email = StringField('Email:', validators=[validators.DataRequired(), validators.Email()])
    # mensagem = StringField('Mensagem:', validators=[validators.DataRequired(), validators.Length(min=10)])
    
    
@app.route('/login') ##rota para fazer o login
def pagina_login():
    
    # bd =conecta_no_banco_de_dados()
    # email = request.form.get('email')
    # senha = request.form.get('senha')
    # cursor = bd.cursor()
    # cursor.execute("""
    #         SELECT *
    #         FROM usuarios
    #         WHERE email = %s AND senha = %s;
    #     """, (email, senha,))
    # usuario = cursor.fetchone()
    # cursor.close()
    # bd.close()
    return render_template('login.html')

@app.route('/cadastro') ##rota para fazer o cadastro caso o usuario n possua cadastro
def fazer_cadastro():
    return render_template('cadastro.html')





@app.route('/confirmacao', methods=['GET', 'POST'])
def contato():
    form = FormularioCadastro()


    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        mensagem = form.mensagem.data    
   
        
        try:
            
            bd =conecta_no_banco_de_dados()
      
            
            cursor = bd.cursor()
            sql = "INSERT INTO contatos (nome, email) VALUES (%s, %s)"
            values = (nome, email, mensagem)
            cursor.execute(sql, values)
            bd.commit()

            print(f"Dados do formulário salvos com sucesso!")
            
        finally:
            if bd is not None:
             bd.close()

app.run()