from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, validators
from typing import NotRequired
# from bd_config import conecta_no_banco_de_dados

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




class FormularioContato(FlaskForm):
    nome = StringField('Nome:', validators=[validators.DataRequired()])
    email = StringField('Email:', validators=[validators.DataRequired(), validators.Email()])
    mensagem = StringField('Mensagem:', validators=[validators.DataRequired(), validators.Length(min=10)])
    
    
@app.route('/login') ##rota para fazer o login
def pagina_login():
    return render_template('login.html')

@app.route('/cadastro') ##rota para fazer o cadastro caso o usuario n possua cadastro
def fazer_cadastro():
    return render_template('cadastro.html')


app.run()