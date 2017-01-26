import os
import sqlite3 as sql


# Obtem todas as SUB REQUISICOES nao classificadas
db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    procs_new = conn.execute("select * from sub_request_content as sc where sc.id_email is null;")
    class_req = procs_new.fetchall()

# Estrutura somente as informacoes comparaveis entre emails e requisicoes
# Obtem todos os EMAILS classificados
with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    procs_new = conn.execute("select * from email_content;")
    class_email = procs_new.fetchall()

# Estrutura somente as informacoes comparaveis entre emails e requisicoes
#email_string = [x[6:22] for x in class_email]

cont = 1
for email in class_email:
    for req in class_req:
        flag = set(req[5:21]) & set(email[5:21])
        if req[5:21] == email[5:21]:
            print("found", cont, email[0:3])
            cont = cont + 1

            with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                # Atualiza tabela sub_request_content
                conn.execute("update sub_request_content set id_email=? where id_sub=?", (email[1], req[1]))
                # Atualiza endereco dos arquivos de email na tabela
                conn.execute("update sub_requests_queue_statuses set emaill_file_path=? where id_sub=?", (email[3], req[1]))
                # Atualiza nome dos arquivos de email na tabela
                conn.execute("update sub_requests_queue_statuses set emaill_file_name=? where id_sub=?", (email[2], req[1]))
                conn.commit()

        else:
            pass
