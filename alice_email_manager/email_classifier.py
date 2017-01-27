#! /usr/bin/python
# -*- coding: latin-1 -*-
from xlrd import open_workbook
import sqlite3 as sql
import os
import time
import re


# Li linha a linha do excel
def readRows(sheet):
    # using list comprehension
    return [sheet.row_values(idx) for idx in range(sheet.nrows)]


# Dado uma string, retorna somente os numeros
def trata_numeros(ncm_string):
    # print "string_ncm: ", type(ncm_string), ncm_string
    value = re.findall(r'\d+', ncm_string)
    # print "imprime ncms tratados: ", ncm
    return value


def trata_ncm(ncm_string):
    # print "string_ncm: ", type(ncm_string), ncm_string
    ncm = [x[0:x.index(' - ')] for x in ncm_string.split(" até ")]
    # ncm = re.findall(r'\d+', ncm_string)
    # print "imprime ncms tratados: ", ncm
    return ncm


# Checar se existe arquivo com analysis_status NULL
# conn = sql.connect('/usr/lib/cgi-bin/email_app/alice_email_manager/email_tracker.db')
db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    procs_query = conn.execute(
        '''select * from download_inventory where unzip_status = 1 AND analysis_status is null;''')
    procs = procs_query.fetchall()

# Obtem pasta corrente
current_path = os.path.dirname(os.path.realpath(__file__))
attachment_files = current_path + "/unziped_attachments"

# Inicia processo de leitura do arquivo
n_arquivo = 1
data_arq = []
for file in procs:
    # Constroi o endereco do arquivo
    file_name_dir = file[1][:len(file[1]) - 4]
    file_name = file[2]
    file_address = attachment_files + '/' + file_name_dir + '/' + file_name

    # Abre o arquivo
    book = open_workbook(file_address, on_demand=True)
    print("arquivo numero: ", n_arquivo, " - ", file)
    data = []
    # try:
    # O header dos dados fica na primeira aba do arquivo extraido
    sheet_1 = book.sheet_by_name('Aliceweb_parte_1')
    nrow = 0
    row_inicio = None
    # o Header deve ser construido somente com as infomarções da primeira aba
    for cell in sheet_1.col(0):
        # Inicio dos dados (sem cabeçalho)
        codigo = 'Código'
        if codigo in cell.value:
            row_inicio = nrow
        nrow += 1

    # Separa o header
    header_raw = sheet_1.col(0)[0:row_inicio]

    # Inicia a classificacao do arquivo do aliceweb - valores default
    email_id = file[0]
    attachment_file_name = file_name
    file_address = file_address = attachment_files + '/' + file_name_dir
    date_read = str(time.strftime("%d/%m/%Y %H:%M:%S"))
    sentido_trade = None
    tipo_ncm = None
    modo_ncm = None
    lista_ncm = None
    bloco = None
    pais = None
    uf = None
    porto = None
    via = None
    primeiroDetalhamento = None
    segundoDetalhamento = None
    P1 = None
    P2 = None
    P3 = None
    P4 = None
    P5 = None
    P6 = None

    # Inicia a classificacao das informacoes
    for row in header_raw:
        # Sentido imp ou exp
        importacao = 'IMPORTAÇÃO'
        if importacao in row.value:
            # sentido_trade = 'Importação'
            sentido_trade = 'Importação'

        exportacao = 'EXPORTAÇÃO'
        if exportacao in row.value:
            # sentido_trade = 'Exportação'
            sentido_trade = 'Exportação'

        # Caso o metodo de input foi ncm por ncm - Cesta de produtos
        cesta_produtos = 'Cesta de Produtos'
        if 'Cesta de Produtos' in row.value.split(':  ')[0]:
            lista_ncm = str(trata_ncm(row.value.split(':  ')[1]))
            tipo_ncm = 'NCM 8 dígitos'

            # obtem tipo ncm
            db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                procs_new = conn.execute(
                    "select description_portugues from ids_aliceweb as s where s.campo_id = 'modo_ncm' and s.value = ?;",
                    ('unitario',))
                modo_ncm_att = procs_new.fetchall()

            modo_ncm = ''.join(modo_ncm_att[0]).strip()

        # Caso o metodo de input foi intervalo de NCMs - Capítulo -
        digitos = 'dígitos'
        if digitos in row.value.split(':  ')[0]:
            # Obtem a lista ncm
            lista_ncm = str(trata_ncm(row.value.split(':  ')[1]))
            tipo_ncm = ''.join(row.value.split(':  ')[0]).strip()

            # obtem tipo ncm
            db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                procs_new = conn.execute(
                    "select description_portugues from ids_aliceweb as s where s.campo_id = 'modo_ncm' and s.value = ?;",
                    ('intervalo',))
                modo_ncm_att = procs_new.fetchall()

            # print ''.join(modo_ncm_att[0])
            modo_ncm = ''.join(modo_ncm_att[0]).strip()

        # Bloco economico
        bloco_economico = 'Bloco Econômico'
        if bloco_economico in row.value.split(':  ')[0]:
            bloco = row.value.split(':  ')[1].strip()

        # Pais
        pais_var = 'País'
        if pais_var in row.value.split(':  ')[0]:
            pais = row.value.split(':  ')[1].strip()

        # UF
        uf_var = 'UF'
        if uf_var in row.value.split(':  ')[0]:
            uf = row.value.split(':  ')[1].strip()

        # Porto
        porto_var = 'Porto'
        if porto_var in row.value.split(':  ')[0]:
            porto_aux = row.value.split(':  ')[1].split(' - ')
            porto = str(porto_aux[0]).strip()
        # Via
        via_var = 'Via'
        if 'Via' in row.value.split(':  ')[0]:
            via = row.value.split(':  ')[1].strip()

        # Primeiro Detalhamento
        if "Primeiro detalhamento" in row.value.split(':  ')[0]:
            primeiroDetalhamento = row.value.split(':  ')[1].strip()

        # Segundo Detalhamento
        if "Segundo detalhamento" in row.value.split(':  ')[0]:
            segundoDetalhamento = row.value.split(':  ')[1].strip()

        # P1
        if "P1" in row.value.split(':  ')[0]:
            P1 = trata_numeros(row.value.split(':  ')[1])
            P1 = str(P1[1]) + str(P1[0]) + " - " + str(P1[3]) + str(P1[2])

        # P2
        if "P2" in row.value.split(':  ')[0]:
            P2 = trata_numeros(row.value.split(':  ')[1])
            P2 = str(P2[1]) + str(P2[0]) + " - " + str(P2[3]) + str(P2[2])

        # P3
        if "P3" in row.value.split(':  ')[0]:
            P3 = trata_numeros(row.value.split(':  ')[1])
            P3 = str(P3[1]) + str(P3[0]) + " - " + str(P3[3]) + str(P3[2])

        # P4
        if "P4" in row.value.split(':  ')[0]:
            P4 = trata_numeros(row.value.split(':  ')[1])
            P4 = str(P4[1]) + str(P4[0]) + " - " + str(P4[3]) + str(P4[2])

        # P5
        if "P5" in row.value.split(':  ')[0]:
            P5 = trata_numeros(row.value.split(':  ')[1])
            P5 = str(P5[1]) + str(P5[0]) + " - " + str(P5[3]) + str(P5[2])

        # P6
        if "P6" in row.value.split(':  ')[0]:
            P6 = trata_numeros(row.value.split(':  ')[1])
            P6 = str(P6[1]) + str(P6[0]) + " - " + str(P6[3]) + str(P6[2])

    # Coloca informacoes em formato de vetor
    info_row = [(
        email_id, attachment_file_name, file_address, date_read, sentido_trade, tipo_ncm, modo_ncm, str(lista_ncm),
        bloco,
        pais, uf, porto, via, primeiroDetalhamento, segundoDetalhamento, P1, P2, P3, P4, P5, P6)]

    '''
    print(type(email_id), email_id)
    print(type(attachment_file_name), attachment_file_name)
    print(type(file_address), file_address)
    print(type(date_read), date_read)
    print(type(sentido_trade), sentido_trade)
    print(type(tipo_ncm), tipo_ncm)
    print(type(modo_ncm), modo_ncm)
    print(type(lista_ncm), lista_ncm)
    print(type(bloco), bloco)
    print(type(pais), pais)
    print(type(uf), uf)
    print(type(porto), porto)
    print(type(via), via)
    print(type(primeiroDetalhamento), primeiroDetalhamento)
    print(type(segundoDetalhamento), segundoDetalhamento)
    print(type(P1), P1)
    print(type(P2), P2)
    print(type(P3), P3)
    print(type(P4), P4)
    print(type(P5), P5)
    print(type(P6), P6)
    '''

    # Verifica se as caracteristicas basicas de uma requicao foram atendidas
    if sentido_trade == None:
        # Atualiza status na tabela download inventory
        # conn = sql.connect('/usr/lib/cgi-bin/email_app/alice_email_manager/email_tracker.db')
        db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            conn.execute("update download_inventory set analysis_status=? where email_id=?", (3, email_id))
            conn.execute("update download_inventory set data_analysis=? where email_id=?",
                         (str(time.strftime("%d/%m/%Y %H:%M:%S")), email_id))
            conn.commit()

    else:
        # Atualiza a tabela de email_content
        # conn = sql.connect('/usr/lib/cgi-bin/email_app/alice_email_manager/email_tracker.db')
        db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            conn.text_factory = str
            cur = conn.cursor()
            cur.executemany(
                '''INSERT INTO email_content(
                    email_id, attachment_file_name, file_address, date_read
                    , sentido_trade, tipo_ncm, modo_ncm, lista_ncm, bloco
                   , pais, uf, porto, via, primeiroDetalhamento, segundoDetalhamento
                    , P1, P2, P3, P4, P5, P6)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
                info_row)
            conn.commit()

        # Atualiza status na tabela download inventory
        # conn = sql.connect('/usr/lib/cgi-bin/email_app/alice_email_manager/email_tracker.db')
        db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            conn.execute("update download_inventory set analysis_status=? where email_id=?", (1, email_id))
            conn.execute("update download_inventory set data_analysis=? where email_id=?",
                         (str(time.strftime("%d/%m/%Y %H:%M:%S")), email_id))
            conn.commit()
