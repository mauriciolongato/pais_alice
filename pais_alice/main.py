# -*- coding: latin-1 -*-
from selenium import webdriver
import os
import time
import sqlite3 as sql
from pyvirtualdisplay import Display

from helpers import drive_browser
from helpers import data_input
from helpers import dir_manager as dm
from selenium.webdriver.chrome.options import Options

# Define os filtros
main_path = os.path.dirname(os.path.realpath(__file__))
db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
input_address = main_path + '/users_sub_requests'
output_address = main_path + '/reports'
tolerancia_erro = 2


# Busca requisicao que esta em andamento
with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    procs_query = conn.execute('''select ss.*
                                from        sub_requests_queue_statuses as ss
                                inner join requests_queue_statuses          as   rs on ss.id_request = rs.id
                                where rs.req_status = 1 and ss.req_status = 1;''')
    procs = procs_query.fetchall()

with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    # Obtem a fila de espera para processamento
    procs_new = conn.execute('''select ss.*
                                from        sub_requests_queue_statuses as ss
                                inner join requests_queue_statuses          as   rs on ss.id_request = rs.id
                                where rs.req_status = 1 and ss.req_status = 0;''')
    requests = procs_new.fetchall()

with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    # Obtem a lista de erros com quantidade menor que criterio predefinido
    procs_erros = conn.execute('''select ss.*
                                from        sub_requests_queue_statuses as ss
                                inner join requests_queue_statuses          as   rs on ss.id_request = rs.id
                                where rs.req_status = 1 and ss.req_status = 3 and qt_erros <=?;''', (str(tolerancia_erro), ))
    requests_erro = procs_erros.fetchall()

# obtem a lista de usuarios processando atualmente no servidor
users_running = list(set([req[3] for req in procs]))
# Obtem a lista de candidatos a serem rodados
requests_list = list(set([req[3] for req in requests]))

# Obtem a requisicao que irá ser rodada
try:
    requests = requests + requests_erro
    candidates_requests = min([x for x in requests if x not in users_running])
    file_name = candidates_requests[6]
except:
    file_name = None

# Dado que temos um candidato, altera o status
# print "id da requisicao: ", candidates_requests[0]

# Trata a requisicao
print(file_name)
if file_name:

    requisicao = data_input.open_json(input_address +"/" + file_name)
    start_time = str(time.strftime("%d/%m/%Y %H:%M:%S"))
    # conn.execute("update requests_queue_statuses set req_status=? where Id=?", (1, candidates_requests[0]))
    with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
        conn.execute("update sub_requests_queue_statuses set req_status=? where id_sub=?", (1, candidates_requests[0]))
        conn.execute("update sub_requests_queue_statuses set req_start_time=? where id_sub=?", (start_time, candidates_requests[0]))
        conn.commit()

    # Cria a estrutura de pastas para as requisicoes
    output_request_dir = dm.create_dir(file_name.split("_sub_")[0], output_address)

    # Separa nas informacoes para a simulacao
    pipe_exec = requisicao['pipe']
    list_periodo = requisicao['periodo']
    list_ncm = requisicao['ncm']

    # Atualiza onde fica a root
    main_path = output_request_dir

    # Guarda na memoria a acao do sistema
    error_flag = "1. acesso site"

    # Conta a requisicao (agora e o numero da sub)
    count_requisicao = 0
    # Inicio da insercao dos dados

    try:
        #display = Display(visible=0, size=(1024, 1024))
        #display.start()
        print("configurou o display")
        service_args = ['--load-images=no']
        driver = webdriver.PhantomJS(service_args=service_args)
        driver.get('http://aliceweb.mdic.gov.br/');
        time.sleep(3)

        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_0.png")
        print("acessou o site do aliceweb")
        error_flag = "2. Login"
        drive_browser.exec_login(driver, pipe_exec)             # 1. Faz login no site
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_1.png")
        print("fez login")

        # Escolhe a lingua - pt
        driver.find_element_by_id("pt").click()
        print("definiu portugues")
        time.sleep(10)

        error_flag = "3. Definiu Pesquisa"
        drive_browser.exec_define_pesquisa(driver, pipe_exec)   # 2. Imp/Exp/Total - Funcao incompleta
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_2.png")
        print("definiu pesquisa")
        error_flag = "4. Insere NCM"
        # Insere os NMCs
        drive_browser.exec_insere_nmc(driver, list_ncm, pipe_exec)
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_3.png")
        print("inseriu ncm")
        error_flag = "5. Bloco Economico"
        # Insere Bloco Economico
        drive_browser.exec_insere_bloco_economico(driver, pipe_exec)
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_4.png")
        print("inseriu bloco economico")
        error_flag = "6. Pais"
        # Pais
        drive_browser.exec_insere_pais(driver, pipe_exec)
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_5.png")
        print("inseriu pais")
        error_flag = "7. Estado"
        # Estado
        drive_browser.exec_insere_estado(driver, pipe_exec)
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_6.png")
        print("inseriu Estado")
        error_flag = "8. Portos"
        # Insere PORTOS
        drive_browser.exec_insere_porto(driver, pipe_exec)
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_7.png")
        print("inseriu Portos")
        error_flag = "9. Vias"
        # Vias
        drive_browser.exec_insere_vias(driver, pipe_exec)
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_8.png")
        print("inseriu Vias")
        error_flag = "10. Detalhamento"
        # Insere detalhamentos
        drive_browser.exec_insere_detalhamentos(driver, pipe_exec)
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_9.png")
        print("inseriu detalhamentos")
        error_flag = "11. Periodo"
        # Define periodos
        drive_browser.exec_insere_periodos(driver, list_periodo, pipe_exec)
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_10.png")
        print("inseriu periodo")
        error_flag = "12. Botao Pesquisar"

        # Finaliza a pesquisa
        driver.find_element_by_id('btnPesquisar').click()       # Clica no botao para fazer a pesquisa
        time.sleep(3)                                           # Espera um tempo para renderizar a pagina
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_11.png")
        print("iniciou pesquisas")

        # Clica no botao de enviar
        driver.find_element_by_id('btnGerar').click()
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_12.png")
        print("Requisitou arquivo por email")

        # Clica no tipo excel
        time.sleep(30)
        driver.find_element_by_id('arquivoExcel').click()
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_13.png")
        print("Definiu formato excel")

        # Clica enviar
        driver.find_element_by_id('btnGerarArquivo').click()
        driver.save_screenshot(output_request_dir+"/"+"screen_img/"+file_name+'_'+str(count_requisicao)+"_14.png")
        print("Deu ok")

        # Caso tudo tenha rodado corretamente, atualiza a sub
        print("atualiza DB")
        # Atualiza que acabou o processamento da requisicao
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            conn.execute("update sub_requests_queue_statuses set req_status=? where id_sub=?", (2, candidates_requests[0]))
            end_time = str(time.strftime("%d/%m/%Y %H:%M:%S"))
            conn.execute("update sub_requests_queue_statuses set req_end_time=? where id_sub=?", (end_time, candidates_requests[0]))
            conn.commit()

        #Fecha o browser
        driver.quit()

    except:
        # Atualiza o status da sub_request
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            conn.execute("update sub_requests_queue_statuses set req_status=? where id_sub=?", (3, candidates_requests[0]))
            conn.execute("update sub_requests_queue_statuses set etapa_ultimo_erro=? where id_sub=?", (3, error_flag))

        # Obtem a quantidade de erros anteriores
        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            current_task = conn.execute("select qt_erros from sub_requests_queue_statuses as ss where id_sub=?", (str(candidates_requests[0]),))
            requests = current_task.fetchall()
            qt_error = int(requests[0][0]) + 1

        with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
            conn.execute("update sub_requests_queue_statuses set qt_erros=? where id_sub=?", (qt_error, candidates_requests[0]),)
            conn.commit()

        driver.save_screenshot(output_request_dir+"/"+"screen_img/print_erro.png")
        driver.quit()
        #display.stop()
