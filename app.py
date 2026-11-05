import re
from datetime import date, timedelta
from pathlib import Path

import click
import pymysql
from cryptography.fernet import Fernet
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
cifra = Fernet(app.config['CPF_KEY'].encode())


def conectar(usar_banco=True):
    return pymysql.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME'] if usar_banco else None,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
    )


def buscar(sql, dados=()):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql, dados)
            return cursor.fetchall()
    finally:
        conexao.close()


def salvar(sql, dados=()):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql, dados)
        conexao.commit()
        return True
    except pymysql.IntegrityError:
        conexao.rollback()
        return False
    finally:
        conexao.close()


def limpar_cpf(cpf):
    return cpf.replace('.', '').replace('-', '').replace(' ', '')


def criptografar_cpf(cpf):
    return cifra.encrypt(cpf.encode()).decode()


def email_valido(email):
    return bool(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email)) and len(email) <= 120


def formatar_horario(horario):
    if isinstance(horario, timedelta):
        segundos = int(horario.total_seconds())
        return f'{segundos // 3600:02d}:{segundos % 3600 // 60:02d}'
    return str(horario)[:5]


def formatar_data(valor):
    if isinstance(valor, date):
        return valor.strftime('%d/%m/%Y')
    return str(valor)


app.jinja_env.filters['horario'] = formatar_horario
app.jinja_env.filters['data_br'] = formatar_data


@app.errorhandler(pymysql.MySQLError)
def erro_banco(erro):
    app.logger.error('Falha no MySQL: %s', erro)
    return render_template(
        'erro.html',
        titulo='Banco de dados indisponível',
        mensagem='Não foi possível acessar o banco. Confira se o MySQL está ligado '
                 'e se os dados de conexão no arquivo .env estão corretos.',
    ), 503


@app.errorhandler(404)
def nao_encontrado(erro):
    return render_template(
        'erro.html', titulo='Registro não encontrado',
        mensagem='A página ou o registro solicitado não foi encontrado.',
    ), 404


@app.before_request
def ver_login():
    endpoints_publicos = {'login', 'static'}
    if request.endpoint and request.endpoint not in endpoints_publicos and 'id_usuario' not in session:
        return redirect(url_for('login'))


@app.context_processor
def nome_usuario():
    return {'nome_usuario': session.get('nome', '')}


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'id_usuario' in session:
        return redirect(url_for('inicio'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        usuarios = buscar('SELECT * FROM usuarios WHERE email=%s', (email,))

        if usuarios and check_password_hash(usuarios[0]['senha_hash'], senha):
            session.clear()
            session.permanent = True
            session['id_usuario'] = usuarios[0]['id']
            session['nome'] = usuarios[0]['nome']
            return redirect(url_for('inicio'))

        flash('E-mail ou senha incorretos.', 'danger')

    return render_template('login.html')


@app.route('/sair', methods=['POST'])
def sair():
    session.clear()
    return redirect(url_for('login'))


@app.route('/painel')
def inicio():
    contagens = {
        'tutores': buscar('SELECT COUNT(*) total FROM tutores')[0]['total'],
        'pets': buscar('SELECT COUNT(*) total FROM pets')[0]['total'],
        'agendamentos': buscar('SELECT COUNT(*) total FROM agendamentos')[0]['total'],
    }
    return render_template('dashboard.html', contagens=contagens)

# Tutores - CRUD

@app.route('/tutores')
def listar_tutores():
    busca = request.args.get('q', '').strip()
    lista = buscar(
        'SELECT id,nome,email,telefone FROM tutores WHERE nome LIKE %s ORDER BY nome',
        ('%' + busca + '%',),
    )
    return render_template('tutores.html', rows=lista, q=busca)


@app.route('/tutores/novo', methods=['GET', 'POST'])
@app.route('/tutores/<int:id_tutor>/editar', methods=['GET', 'POST'])
def salvar_tutor(id_tutor=None):
    antigo = None
    if id_tutor:
        dados = buscar('SELECT * FROM tutores WHERE id=%s', (id_tutor,))
        if dados:
            antigo = dados[0]
        else:
            abort(404)

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = limpar_cpf(request.form.get('cpf', ''))
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()

        if not nome or len(nome) > 100 or not email_valido(email) or len(telefone) > 20:
            flash('Confira o nome, o e-mail e o telefone.', 'danger')
        elif (not id_tutor or cpf) and (len(cpf) != 11 or not cpf.isascii() or not cpf.isdigit()):
            flash('Informe o CPF com 11 números.', 'danger')
        else:
            if id_tutor:
                if cpf:
                    ok = salvar(
                        'UPDATE tutores SET nome=%s, cpf_criptografado=%s, email=%s, telefone=%s WHERE id=%s',
                        (nome, criptografar_cpf(cpf), email, telefone, id_tutor),
                    )
                else:
                    ok = salvar(
                        'UPDATE tutores SET nome=%s, email=%s, telefone=%s WHERE id=%s',
                        (nome, email, telefone, id_tutor),
                    )
            else:
                ok = salvar(
                    'INSERT INTO tutores(nome,cpf_criptografado,email,telefone) VALUES(%s,%s,%s,%s)',
                    (nome, criptografar_cpf(cpf), email, telefone),
                )

            if ok:
                flash('Tutor salvo.', 'success')
                return redirect(url_for('listar_tutores'))

            flash('Não foi possível salvar. Confira se o e-mail já está cadastrado.', 'danger')

    return render_template('tutor_form.html', antigo=antigo)


@app.route('/tutores/<int:id_tutor>/excluir', methods=['POST'])
def excluir_tutor(id_tutor):
    if salvar('DELETE FROM tutores WHERE id=%s', (id_tutor,)):
        flash('Tutor excluído.', 'success')
    else:
        flash('Este tutor possui pets ou agendamentos cadastrados. Exclua os vínculos antes de remover o tutor.', 'danger')
    return redirect(url_for('listar_tutores'))

# Pets - CRUD

@app.route('/pets')
def listar_pets():
    busca = request.args.get('q', '').strip()
    lista = buscar(
        '''
        SELECT p.id, p.nome, p.especie, p.raca, p.peso, p.id_tutor, t.nome AS tutor
        FROM pets p
        LEFT JOIN tutores t ON t.id = p.id_tutor
        WHERE p.nome LIKE %s
        ORDER BY p.nome
        ''',
        ('%' + busca + '%',),
    )
    return render_template('pets.html', rows=lista, q=busca)


@app.route('/pets/novo', methods=['GET', 'POST'])
@app.route('/pets/<int:pet_id>/editar', methods=['GET', 'POST'])
def salvar_pet(pet_id=None):
    tutores = buscar('SELECT id,nome FROM tutores ORDER BY nome')
    antigo = None
    if pet_id:
        dados = buscar('SELECT * FROM pets WHERE id=%s', (pet_id,))
        if dados:
            antigo = dados[0]
        else:
            abort(404)

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        especie = request.form.get('especie', '').strip()
        raca = request.form.get('raca', '').strip()
        peso = request.form.get('peso', '').strip()
        tutor_id = request.form.get('tutor_id', '').strip()

        if not nome or len(nome) > 100 or not especie or len(especie) > 50 or not raca or len(raca) > 120 or len(peso) > 20:
            flash('Confira os dados do pet (nome, espécie, raça e peso).', 'danger')
        elif not tutor_id:
            flash('Selecione o tutor do pet.', 'danger')
        else:
            if pet_id:
                ok = salvar(
                    'UPDATE pets SET nome=%s, especie=%s, raca=%s, peso=%s, id_tutor=%s WHERE id=%s',
                    (nome, especie, raca, peso, tutor_id, pet_id),
                )
            else:
                ok = salvar(
                    'INSERT INTO pets(nome,especie,raca,peso,id_tutor) VALUES(%s,%s,%s,%s,%s)',
                    (nome, especie, raca, peso, tutor_id),
                )

            if ok:
                flash('Pet salvo.', 'success')
                return redirect(url_for('listar_pets'))

            flash('Não foi possível salvar o pet.', 'danger')

    return render_template('pet_form.html', antigo=antigo, tutores=tutores)


@app.route('/pets/<int:pet_id>/excluir', methods=['POST'])
def excluir_pet(pet_id):
    if salvar('DELETE FROM pets WHERE id=%s', (pet_id,)):
        flash('Pet excluído.', 'success')
    else:
        flash('Este pet tem agendamentos cadastrados. Exclua os agendamentos antes de remover o pet.', 'danger')
    return redirect(url_for('listar_pets'))

# Agendamentos - CRUD

@app.route('/agendamentos')
def listar_agendamentos():
    lista = buscar(
        '''
        SELECT ag.id, ag.tutor_id, ag.pet_id, ag.objetivo, ag.data, ag.horario, ag.observacao,
               t.nome AS tutor, t.email, t.telefone,
               p.nome AS pet, p.especie, p.raca, p.peso
        FROM agendamentos ag
        JOIN tutores t ON ag.tutor_id = t.id
        JOIN pets p ON ag.pet_id = p.id
        ORDER BY ag.data, ag.horario
        '''
    )
    return render_template('agendamentos.html', rows=lista)

@app.route('/agendamentos/novo', methods=['GET', 'POST'])
@app.route('/agendamentos/<int:ag_id>/editar', methods=['GET', 'POST'])
def salvar_agendamento(ag_id=None):
    tutores = buscar('SELECT id,nome FROM tutores ORDER BY nome')
    pets = buscar(
        '''
        SELECT p.id, p.nome, p.id_tutor, t.nome AS tutor
        FROM pets p
        JOIN tutores t ON t.id = p.id_tutor
        ORDER BY p.nome
        '''
    )
    antigo = None
    if ag_id:
        dados = buscar('SELECT * FROM agendamentos WHERE id=%s', (ag_id,))
        if dados:
            antigo = dados[0]
            antigo['horario'] = formatar_horario(antigo['horario'])
        else:
            abort(404)

    if request.method == 'POST':
        tutor_id = request.form.get('tutor_id', '').strip()
        pet_id = request.form.get('pet_id', '').strip()
        objetivo = request.form.get('objetivo', '').strip()
        data = request.form.get('data', '').strip()
        horario = request.form.get('horario', '').strip()
        observacao = request.form.get('observacao', '').strip()

        pet_valido = False
        if tutor_id.isdigit() and pet_id.isdigit():
            vinculo = buscar('SELECT id FROM pets WHERE id=%s AND id_tutor=%s', (pet_id, tutor_id))
            pet_valido = bool(vinculo)

        if not (tutor_id and pet_id and objetivo and len(objetivo) <= 100 and data and horario):
            flash('Preencha todos os campos obrigatórios do agendamento.', 'danger')
        elif not pet_valido:
            flash('O pet selecionado não pertence ao tutor informado.', 'danger')
        else:
            if ag_id:
                ok = salvar(
                    'UPDATE agendamentos SET tutor_id=%s, pet_id=%s, objetivo=%s, data=%s, horario=%s, observacao=%s WHERE id=%s',
                    (tutor_id, pet_id, objetivo, data, horario, observacao, ag_id),
                )
            else:
                ok = salvar(
                    'INSERT INTO agendamentos(tutor_id,pet_id,objetivo,data,horario,observacao) VALUES(%s,%s,%s,%s,%s,%s)',
                    (tutor_id, pet_id, objetivo, data, horario, observacao),
                )

            if ok:
                flash('Agendamento salvo.', 'success')
                return redirect(url_for('listar_agendamentos'))

            flash('Não foi possível salvar o agendamento.', 'danger')

    return render_template('agendamentos_form.html', antigo=antigo, tutores=tutores, pets=pets)


@app.route('/agendamentos/<int:ag_id>/excluir', methods=['POST'])
def excluir_agendamento(ag_id):
    if salvar('DELETE FROM agendamentos WHERE id=%s', (ag_id,)):
        flash('Agendamento excluído.', 'success')
    return redirect(url_for('listar_agendamentos'))


@app.cli.command('iniciar-banco')
def iniciar_banco():
    """Cria o banco e as tabelas sem apagar registros existentes."""
    banco = app.config['DB_NAME']
    if not re.fullmatch(r'[A-Za-z0-9_]{1,64}', banco):
        raise click.ClickException('Use apenas letras, números e _ no nome do banco.')

    sql = Path(__file__).with_name('saep_db.sql').read_text(encoding='utf-8')
    sql = '\n'.join(linha for linha in sql.splitlines() if not linha.lstrip().startswith('--'))
    sql = sql.replace('saep_db', f'`{banco}`')
    try:
        conexao = conectar(usar_banco=False)
        try:
            with conexao.cursor() as cursor:
                for comando in sql.split(';'):
                    if comando.strip():
                        cursor.execute(comando)
            conexao.commit()
        finally:
            conexao.close()
    except pymysql.MySQLError as erro:
        raise click.ClickException(f'Não foi possível preparar o MySQL: {erro}') from erro
    click.echo(f'Banco {banco} pronto.')


@app.cli.command('criar-usuario')
@click.option('--nome', prompt='Nome', default='Administrador')
@click.option('--email', prompt='E-mail', default='admin@saep_db.local')
@click.option('--senha', prompt='Senha', hide_input=True, confirmation_prompt=True)
def criar_usuario(nome, email, senha):
    """Cria um usuário de acesso com senha protegida por hash."""
    nome, email = nome.strip(), email.strip()
    if not nome or len(nome) > 100 or not email_valido(email) or len(senha) < 6:
        raise click.ClickException('Confira nome, e-mail e senha (mínimo de 6 caracteres).')
    try:
        ok = salvar(
            'INSERT INTO usuarios(nome,email,senha_hash) VALUES(%s,%s,%s)',
            (nome, email, generate_password_hash(senha)),
        )
    except pymysql.MySQLError as erro:
        raise click.ClickException(f'Não foi possível acessar o MySQL: {erro}') from erro
    if not ok:
        raise click.ClickException('Já existe um usuário com este e-mail.')
    click.echo('Usuário criado.')

if __name__ == '__main__':
    app.run(debug=True)

