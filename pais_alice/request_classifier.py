import os
import sqlite3 as sql
from helpers import data_input


def get_numeros(ncm_string):
    # print "string_ncm: ", type(ncm_string), ncm_string
    # ncm = ncm_string.lstrip()
    ncm = ncm_string.strip()
    return ncm

# Mapeia as pastas do sistema
main_path = os.path.dirname(os.path.realpath(__file__))
db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
input_address = main_path + '/users_requests'
input_address = main_path + '/users_sub_requests'

# Conecta na base e obtem os requests com suas subs nao mapeadas
with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    procs_new = conn.execute(
        "select * from sub_requests_queue_statuses as s where s.req_status = 2 and s.req_classifier_status is null;")
    requests = procs_new.fetchall()

# Inicia a classificacao de cada requisicao
for requisicao in requests:
    id_sub = requisicao[0]
    id_request = requisicao[1]
    req_file_name = requisicao[6]
    print(req_file_name)

    # obtem o json do arquivo
    requisicao_file = data_input.open_json(input_address + "/" + req_file_name)

    # obtem informacao
    pipe_exec = requisicao_file['pipe']
    list_periodo = requisicao_file['periodo']
    list_ncm = requisicao_file['ncm']
    print(list_ncm)

    # sub_request_content
    # id da subrequisicao
    id_sub = requisicao[0]
    # Sentido do trade
    try:
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'imp_exp' and s.value = ?;",
                (pipe_exec['sentido'],))
            sentido_att = procs_new.fetchall()
        sentido_trade = ''.join(sentido_att[0])

    except:
        sentido_trade = None

    # tipo_ncm - se foi pedido intervalo ou unitario de ncm 2, 4, 6 ou 8
    try:
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'tipoNcm' and s.value = ?;",
                (pipe_exec['ncm_tipo'],))
            tipo_ncm_att = procs_new.fetchall()
        tipo_ncm = ''.join(tipo_ncm_att[0])

    except:
        tipo_ncm = None

    # modo_ncm - se a requisicao foi feita por intervalo ou unitario
    try:
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'modo_ncm' and s.value = ?;",
                (pipe_exec['modo_ncm'],))
            modo_ncm_att = procs_new.fetchall()
        modo_ncm = ''.join(modo_ncm_att[0]).strip()

    except:
        modo_ncm = None

    # lista_ncm - contem o vetor de ncms
    try:
        lista_ncm = str(requisicao_file['ncm'])

    except:
        lista_ncm = None

    # bloco - Se a requisicao possui bloco economico
    try:
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'bloco' and s.value = ?;",
                (pipe_exec['bloco_economico'],))
            bloco_att = procs_new.fetchall()
        bloco = pipe_exec['bloco_economico'] + " - " + ''.join(bloco_att[0]).strip()

    except:
        bloco = None

    # pais - Se a requisicao possui pais especificado
    try:
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'pais' and s.value = ?;",
                (pipe_exec['pais'],))
            pais_att = procs_new.fetchall()
        pais = pipe_exec['pais'] + " - " + ''.join(pais_att[0]).strip()

    except:
        pais = None

    # uf - Se a requisicao possui estado especificado
    try:
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'uf' and s.value = ?;",
                (pipe_exec['estado'],))
            uf_att = procs_new.fetchall()
        uf = pipe_exec['estado'] + " - " + ''.join(uf_att[0]).strip()

    except:
        uf = None

    # porto - Se a requisicao possui porto especificado
    try:
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'porto' and s.value = ?;",
                (pipe_exec['porto'],))
            porto_att = procs_new.fetchall()
        porto = pipe_exec['porto']

    except:
        porto = None

    # via - Se a requisicao possui via especificado
    try:
        id_via = get_numeros(pipe_exec['via'])
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'via' and s.value = ?;",
                (str(id_via),))
            via_att = procs_new.fetchall()
        via = str(id_via) + " - " + ''.join(via_att[0]).strip()

    except:
        via = None

    # primeiroDetalhamento - Se a requisicao possui primeiro detalhamento
    try:
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'primeiroDetalhamento' and s.value = ?;",
                (pipe_exec['detalhamento'][0],))
            primeiro_detalhamento_att = procs_new.fetchall()
        primeiroDetalhamento = ''.join(primeiro_detalhamento_att[0]).strip()

    except:
        primeiroDetalhamento = None

    # segundoDetalhamento - Se a requisicao possui segundo detalhamento
    try:
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            procs_new = conn.execute(
                "select description_portugues from ids_aliceweb as s where s.campo_id = 'segundoDetalhamento' and s.value = ?;",
                (pipe_exec['detalhamento'][1],))
            segundo_detalhamento_att = procs_new.fetchall()
        segundoDetalhamento = ''.join(segundo_detalhamento_att[0]).strip()

    except:
        segundoDetalhamento = None

    # P1 - Primeiro periodo
    try:
        P1_att = list_periodo[0]
        P1 = P1_att["periodo-periodoAnoInicio_1"] + P1_att["periodo-periodoMesInicio_1"] + " - " + P1_att[
            "periodo-periodoAnoFinal_1"] + P1_att["periodo-periodoMesFinal_1"]
    except:
        P1 = None

    # P2 - Primeiro periodo
    try:
        P2_att = list_periodo[1]
        P2 = P2_att["periodo-periodoAnoInicio_2"] + P2_att["periodo-periodoMesInicio_2"] + " - " + P2_att[
            "periodo-periodoAnoFinal_2"] + P2_att["periodo-periodoMesFinal_2"]

    except:
        P2 = None

    # P3 - Primeiro periodo
    try:
        P3_att = list_periodo[2]
        P3 = P3_att["periodo-periodoAnoInicio_3"] + P3_att["periodo-periodoMesInicio_3"] + " - " + P3_att[
            "periodo-periodoAnoFinal_3"] + P3_att["periodo-periodoMesFinal_3"]

    except:
        P3 = None

    # P4 - Primeiro periodo
    try:
        P4_att = list_periodo[3]
        P4 = P4_att["periodo-periodoAnoInicio_4"] + P4_att["periodo-periodoMesInicio_4"] + " - " + P4_att[
            "periodo-periodoAnoFinal_4"] + P4_att["periodo-periodoMesFinal_4"]

    except:
        P4 = None

    # P5 - Primeiro periodo
    try:
        P5_att = list_periodo[4]
        P5 = P5_att["periodo-periodoAnoInicio_5"] + P5_att["periodo-periodoMesInicio_5"] + " - " + P5_att[
            "periodo-periodoAnoFinal_5"] + P5_att["periodo-periodoMesFinal_5"]

    except:
        P5 = None

    # P6 - Primeiro periodo
    try:
        P6_att = list_periodo[5]
        P6 = P6_att["periodo-periodoAnoInicio_6"] + P6_att["periodo-periodoMesInicio_6"] + " - " + P6_att[
            "periodo-periodoAnoFinal_6"] + P6_att["periodo-periodoMesFinal_6"]

    except:
        P6 = None

    info_row = [(id_sub, req_file_name, input_address, sentido_trade, tipo_ncm, modo_ncm, lista_ncm, bloco, pais, uf,
                 porto, via, primeiroDetalhamento, segundoDetalhamento, P1, P2, P3, P4, P5, P6)]

    '''
    print type(id_sub), id_sub
    print type(req_file_name), req_file_name
    print type(input_address), input_address
    print type(sentido_trade), sentido_trade
    print type(tipo_ncm), tipo_ncm
    print type(modo_ncm), modo_ncm
    print type(lista_ncm), lista_ncm
    print type(bloco), bloco
    print type(pais), pais
    print type(uf), uf
    print type(porto), porto
    print type(via), via
    print type(primeiroDetalhamento), primeiroDetalhamento
    print type(segundoDetalhamento), segundoDetalhamento
    print type(P1), P1
    print type(P2), P2
    print type(P3), P3
    print type(P4), P4
    print type(P5), P5
    print type(P6), P6
    print '\n'
    '''

    # Atualiza a tabela de email_content
    with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
        conn.text_factory = str
        cur = conn.cursor()
        cur.executemany(
            '''INSERT INTO sub_request_content(
                id_sub, attachment_file_name, file_address, sentido_trade, tipo_ncm, modo_ncm, lista_ncm, bloco
                , pais, uf, porto, via, primeiroDetalhamento, segundoDetalhamento
                , P1, P2, P3, P4, P5, P6)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
            info_row)
        conn.commit()

    # Atualiza status da classificacao na tabela sub_requests_queue_statuses
    with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
        conn.execute("update sub_requests_queue_statuses set req_classifier_status=? where id_sub=?", (2, id_sub))
        conn.commit()