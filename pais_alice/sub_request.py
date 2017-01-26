import os
import json
import time
import sqlite3 as sql

from helpers import data_input

# Define os filtros
# Abre arquivo com dados para extracao
# Obtem pasta corrente
main_path = os.path.dirname(os.path.realpath(__file__))
db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
input_address = main_path + '/users_requests'
output_address = main_path + '/users_sub_requests'

# Conecta na base e obtem os requests com suas subs nao mapeadas
with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    procs_new = conn.execute("select * from requests_queue_statuses as s where s.req_status = 0;")
    requests = procs_new.fetchall()

print("lista requests ", requests)
# obtem a lista de usuarios processando atualmente no servidor
# Obtem a lista de candidatos a serem rodados
# Obtem a requisicao que ira ser rodada
try:
    candidates_requests = [x for x in requests]
    # chama o arquivo de executa o inicio da request
except:
    candidates_requests = []
    pass

# Dado que temos um candidato, altera o status
# print "id da requisicao: ", candidates_requests[0]

# print "arquivos onlyfiles - ", onlyfiles
for candidato in candidates_requests:
    try:
        file_name = candidato[5]
        print('arquivo eleito: ', file_name)
        print('endereco do arquivo: ', input_address + "/" + file_name)
        # Trata a requisicao
        requisicoes = data_input.open_json(input_address + "/" + file_name)
        # print "requisicoes pre process: ", requisicoes
        requisicoes = data_input.open_php(requisicoes)
        # print "requisicoes: ", requisicoes

        count = 0
        for requisicao in requisicoes:
            print(requisicao)
            pipe_exec = requisicao['pipe']
            list_periodo = requisicao['periodo']
            ncm_list = requisicao['ncm']
            if ncm_list == []:
                # Caso o campo ncm tenha vindo vazio
                start_time = str(time.strftime("%d/%m/%Y %H:%M:%S"))

                with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                    # conn.execute("update requests_queue_statuses set req_status=? where Id=?", (1, candidates_requests[0]))
                    conn.execute("update requests_queue_statuses set req_status=? where Id=?", (3, candidato[0]))
                    conn.execute("update requests_queue_statuses set req_start_time=? where Id=?",
                                 (start_time, candidato[0]))
                    conn.commit()
            else:
                exec_lista_ncm = [ncm_list[i:i + 60] for i in range(0, len(ncm_list), 60)]
                requisicao_sub = {}
                for list_ncm in exec_lista_ncm:
                    # Cria o json da requisicao
                    requisicao_sub['pipe'] = pipe_exec
                    requisicao_sub['periodo'] = list_periodo
                    requisicao_sub['ncm'] = list_ncm
                    nome_out = candidato[5] + "_sub_" + str(count)

                    # Salva json da subrequisicao
                    with open(output_address + "/" + nome_out, 'w') as outfile:
                        json.dump(requisicao_sub, outfile)

                    row = candidato
                    with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                        cur = conn.cursor()
                        info_row = [(row[0], str(time.strftime("%d/%m/%Y %H:%M:%S")), row[2], nome_out, row[7], 0)]
                        # print "id_request, user_req_creation_time, aliceweb_user_name, req_file_name, user_email, req_status"
                        # print info_row
                        cur.executemany(
                            '''insert into sub_requests_queue_statuses(id_request, user_req_creation_time, aliceweb_user_name, req_file_name, user_email, req_status) values(?, ?, ?, ?, ?, ?);''',
                            info_row)
                        conn.commit()

                    count += 1

                # Atualiza status da request
                start_time = str(time.strftime("%d/%m/%Y %H:%M:%S"))
                with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                    conn.execute("update requests_queue_statuses set req_status=? where Id=?", (1, candidato[0]))
                    conn.execute("update requests_queue_statuses set req_start_time=? where Id=?",
                                 (start_time, candidato[0]))
                    conn.commit()

    except:
        # Atualiza status da request
        start_time = str(time.strftime("%d/%m/%Y %H:%M:%S"))
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            # conn.execute("update requests_queue_statuses set req_status=? where Id=?", (1, candidates_requests[0]))
            conn.execute("update requests_queue_statuses set req_status=? where Id=?", (3, candidato[0]))
            conn.execute("update requests_queue_statuses set req_start_time=? where Id=?", (start_time, candidato[0]))
            conn.commit()
