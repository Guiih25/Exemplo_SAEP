from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import schema, select
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Usuario, Produto, Movimentacao, db_session
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'luciano123'

# config flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar o sistema'

@login_manager.user_loader
def load_user(user_id):
    return db_session.get(Usuario, int(user_id))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form.get('form_email')
    senha = request.form.get('form_senha')
    if not email:
        flash('Campo email é obrigatorio', 'danger')
        return redirect(url_for('login'))
    if not senha:
        flash('Campo senha é obrigatorio', 'danger')
        return redirect(url_for('login'))

    usuario = db_session.execute(select(Usuario).where(Usuario.email == email)).scalar()
    if usuario and usuario.check_password(senha):
        login_user(usuario)
        return redirect(url_for('dashboard'))
    else:
        flash('Falha na autenticação: Email ou senha incorreto', 'danger')
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/produtos/salvar', methods=['POST'])
@login_required
def salvar_produto():
    id_produto = request.form.get('id_produto')
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    estoque_minimo = request.form.get('estoque_minimo')

    if not nome or not estoque_minimo:
        flash('Erro: nome e estoque minimo são obrigatorio', 'danger')
        return redirect(url_for('salvar_produto'))
    try:

        if id_produto:
            produto = db_session.get(Produto, id_produto)
            produto.nome = nome
            produto.descricao = descricao
            produto.estoque_minimo = estoque_minimo
            flash('Produto atualizado com sucesso', 'success')

        else:
            novo_produto = Produto(
                nome=nome,
                descricao=descricao,
                estoque_minimo=int(estoque_minimo),
            )
            db_session.add(novo_produto)
            flash('Produto salvado com sucesso', 'success')
            db_session.commit()
            return redirect(url_for('dashboard'))

    except Exception as e:
        db_session.rollback()
        flash('Erro', 'danger')

@app.route('/produtos', methods=['GET', 'POST'])
@login_required
def gerenciar_produtos():
    if request.method == 'POST':
        termo_busca = request.form.get('busca')
        busca = select(Produto).where(Produto.nome.like(f'%{termo_busca}%'))
        busca_resultado = db_session.execute(busca).scalars().all()
        return render_template('produtos.html', produtos=busca_resultado)
    lista = select(Produto).order_by(Produto.nome.asc())
    lista_resultado = db_session.execute(lista).scalars().all()
    return render_template('produtos.html', produtos=lista_resultado)

if __name__ == '__main__':
    app.run(debug=True, port=5006)




