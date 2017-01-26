import os
import time
import sqlite3 as sql

from helpers import html_to_data as htd

# Define os filtros
main_path = os.path.dirname(os.path.realpath(__file__))
db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
input_address = main_path + '/users_sub_requests'
output_address = main_path + '/reports'

# Busca requisicao que esta em andamento
print(db_dirpath+'/pais_alice_requests.db')
with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    # Obter as requests que estao em andamento
    procs_query = conn.execute("select * from requests_queue_statuses as rs where rs.req_status = 1;")
    procs = procs_query.fetchall()

id_req_running = list(set([req[0] for req in procs]))
print("idscandidatos ", id_req_running)

for id_req in id_req_running:
    try:
        print("requisicao escolhida ",id_req)
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            qt_subs = conn.execute("select count(*) from sub_requests_queue_statuses as ss where ss.id_request=?", (str(id_req),))
            qt_subs = qt_subs.fetchall()[0]
            qt_subs_done = conn.execute("select count(*) from sub_requests_queue_statuses as ss where id_request=? and emaill_file_name is not null;", (str(id_req),))
            qt_subs_done = qt_subs_done.fetchall()[0]

        print(qt_subs, qt_subs_done)
        if qt_subs == qt_subs_done and qt_subs[0] > 0:
            with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                nome_arquivo = conn.execute("select req_file_name from sub_requests_queue_statuses as ss where id_request=? and req_status=2", (str(id_req),))
                nome_arquivo = nome_arquivo.fetchall()

            # Cria um status intermediario para nao chamar esse processo de novo enquanto nao estiver terminado
            print("nome do arquivo", nome_arquivo)
            output_request_dir = output_address +"/"+nome_arquivo[0][0].split("_sub_")[0]
            print("pasta do output ", output_request_dir)

            # Caso as subs tenham terminado, junte todos os arquivos
            htd.merge_email(id_req, output_request_dir)

            with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                conn.execute("update requests_queue_statuses set req_status=? where Id=?", (2, str(id_req)))
                end_time = str(time.strftime("%d/%m/%Y %H:%M:%S"))
                conn.execute("update requests_queue_statuses set req_end_time=? where Id=?", (end_time, str(id_req)))
                conn.commit()
                time.sleep(10)

            """
            # Caso a requisicao tiver sido processada com sucesso
            print("move arquivo")
            #de = main_path+"/users_requests/"+nome_arquivo[0][0].split("_sub_")[0]
            #para = output_request_dir+"/processed_request"
            #copytree(de, para)
            shutil.move(main_path+"/users_requests/"+nome_arquivo[0][0].split("_sub_")[0], output_request_dir+"/processed_request")

            print("concluido")
            shutil.move(output_request_dir, "/var/www/html/request/output/")
            print("moveu arquivo")
            print("atualiza DB")
            #
            # Alterar essa parte do status da request!!!
            #
            """
    except:
        pass
