from flask import Flask, render_template, request
import sqlite3 as sql
import time
import json
import os

app = Flask(__name__)


@app.route("/")
def pais_alice():
    return render_template('aliceweb.html')


@app.route('/request_info/', methods=['POST'])
def request_info():
    # Cria a requests do DB
    # Define o nome geral da requisicao
    nome_request = "{}_{}_{}".format(str(time.strftime('%Y%m%d')), str(time.strftime("%H%M%S")), request.form['login'])

    # Inicia o processo de criação das requisições
  
    flag_json = create_request_json(request, nome_request)
    flag_db = create_request_db(request, nome_request)

    # Define informacoes para renderizar na pagina da requisição do usuario
    header = ['login', 'email', 'imp_exp', 'modo_ncm', 'tipoNcm', 'comment', 'bloco', 'pais', 'uf', 'porto', 'via',
              'primeiroDetalhamento', 'segundoDetalhamento', 'periodo_extracao',
              'periodo-periodoMesInicio[]', 'periodo-periodoAnoInicio[]',
              'periodo-periodoMesFinal[]', 'periodo-periodoAnoFinal[]']
    data = [request.form[x] for x in header]

    # Obtem a tabela de historico de requisições

    tbl_historico = get_request_queue_statuses()
    header_historico = ['id', 'user_email', 'user_req_creation_time', 'aliceweb_user_name', 'req_start_time',
                        'req_end_time', 'req_status']

    historico = []
    for row in tbl_historico:
        historico.append([row[x] for x in header_historico])
    
    return render_template('result.html', data=data, historico=historico)


@app.route('/admin/')
def admin():

    # Get sub_request status
    tbl_historico = get_sub_request_queue_statuses()
    header_historico = ['id_sub', 'id_request', 'user_email', 'user_req_creation_time', 'aliceweb_user_name',
                        'req_start_time', 'req_end_time', 'req_file_name', 'req_status', 'qt_erros',
                        'req_classifier_status', 'emaill_file_name']
    sub_request_historico = []
    for row in tbl_historico:
        sub_request_historico.append([row[x] for x in header_historico])

    # Get request status
    # Obtem a tabela de historico de requisições
    tbl_historico = get_request_queue_statuses()
    header_historico = ['id', 'user_email', 'user_req_creation_time', 'aliceweb_user_name', 'req_start_time',
                        'req_end_time', 'req_status']
    historico = []
    for row in tbl_historico:
        historico.append([row[x] for x in header_historico])

    return render_template('admin.html', sub_request_historico=sub_request_historico, historico=historico)


def create_request_json(request, nome_request):

    try:
        # Define parametros para criar o arquivo json da requisicao e registrar o pedido no DB
        pipe_exec = dict(login=request.form['login'],
                         senha=request.form['pass'],
                         modo_ncm=request.form['modo_ncm'],
                         bloco_economico=request.form['bloco'],
                         pais=request.form['pais'],
                         estado=request.form['uf'],
                         porto=request.form['porto'],
                         via=request.form['via'],
                         detalhamento=[request.form['primeiroDetalhamento'], request.form['segundoDetalhamento']],
                         sentido=request.form['imp_exp'],
                         ncm_tipo=request.form['tipoNcm'],
                         periodo=request.form['periodo_extracao'])

        datas_id = [{'periodo-periodoAnoInicio': request.form['periodo-periodoAnoInicio[]'],
                     'periodo-periodoMesInicio': request.form['periodo-periodoMesInicio[]'],
                     'periodo-periodoAnoFinal': request.form['periodo-periodoAnoFinal[]'],
                     'periodo-periodoMesFinal': request.form['periodo-periodoMesFinal[]']}]

        data = {'pipe': pipe_exec,
                'periodo': datas_id,
                'ncm': [request.form['comment']]}

        # salva requisicao na pasta requisicoes
        arquivo = './users_requests/'+nome_request
        with open(arquivo, 'w') as outfile:
            json.dump(data, outfile)

        # Caso a criação do arquivo ocorra com sucesso
        nome = arquivo

    except:
        # Caso arquivo nao criado, retorna None
        nome = None

    return nome


def create_request_db(request, nome_request):
    """
    Cria a requisicao na lista de requisicao
    """
    login = request.form['login']
    email = request.form['email']

    db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
        cur = conn.cursor()
        info_row = [(str(time.strftime("%d/%m/%Y %H:%M:%S")), login, nome_request, email, 0)]
        cur.executemany(
            '''insert into requests_queue_statuses(user_req_creation_time,aliceweb_user_name,req_file_name,user_email,req_status) values(?, ?, ?, ?, ?);''',
            info_row)
        conn.commit()


def get_request_queue_statuses():

    db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select * from requests_queue_statuses order by id desc limit 100")
        rows = cur.fetchall();

    return rows


def get_sub_request_queue_statuses():

    db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select * from sub_requests_queue_statuses order by id_request desc limit 200")
        rows = cur.fetchall();

    return rows


def set_flask():
    """
    Interface to start flask server from main
    """
    app.run(host='0.0.0.0',
            port=5010,
            debug=False)


if __name__ == "__main__":
    set_flask()
