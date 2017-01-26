import os
import bs4
import json
import sqlite3 as sql
from xlrd import open_workbook
import pandas as pd
from os import listdir
from os.path import isfile, join


def readRows(sheet):
    # using list comprehension
    return [sheet.row_values(idx) for idx in range(sheet.nrows)]

# obtem pasta atual da execucao
# dir_path = os.path.dirname(os.path.realpath(__file__))
def do_data(dir_path):
    # Define pasta com as informacoes a serem tratadas
    htmls_address = dir_path+"/"+'html'
    pasta_saida = dir_path+"/"+'reports'
    #print "dentro funcao, htmls ", htmls_address
    onlyfiles = [f for f in listdir(htmls_address) if isfile(join(htmls_address, f))]
    # print "arquivos a serem tratados", onlyfiles
    #print onlyfiles
    # 'AliceWeb'
    
    print("nome arquivo geral: {}".format(onlyfiles[0].split('_sub_')[0]))
    file_name = onlyfiles[0].split('_sub_')[0]
    print("file_name (html_to_data): {}".format(file_name))

    onlyfiles = [f for f in onlyfiles]

    # Obtem o header dessa pesquisa - todos os arquivos salvos, possuem o mesmo header, sendo assim, pegarei a informacao
    # com um arquivo arbitrario
    with open(htmls_address +'/'+ onlyfiles[0]) as json_data:
        html = json.load(json_data)
        json_data.close()
    # salva o header
    #ga.salva_header(html, file_name, pasta_saida)


    # Inicia abertura dos arquivos
    print("fez header")
    output_request = []
    for file in onlyfiles:
        print("file: {}".format(file))
        # Abre um arquivo da pasta
        with open(htmls_address+'/'+file) as json_data:
            html = json.load(json_data)
            json_data.close()

        # Parseia as informacoes de cada pagina
        soup = bs4.BeautifulSoup(html, "lxml")
        # Verifica se existe um paginator-lable
        paginator = soup.find_all('label', class_="paginator-label")
        #    print "entra no arquivo ",file, paginator
        if paginator == []:
            print("entrou no paginator zero")
            # Dados nao possuem detalhamento
            # Obtem o header
            header_raw = soup.find(class_="gridSubtitle")
            header = ["numero_pagina"] + [x.text for x in header_raw]
            # A unica pagina a ser apresentada e atual, pois o arquivo nao possui detalhamento
            pg = 1

            # Extrai as informacoes da tabela
            string = soup.select('tr[id*=consulta_simples_row]')  # Obtem informacao
            dados_tbl = [line for line in string]
            for dados in dados_tbl:
                output_request.append([pg] + [x.text for x in dados])


        else:
            print("paginator nao é zero")
            # Nome: numero da pagina -  Cria a estrutura no output
            if len(soup.find_all('label', class_="paginator-label")) > 1:
                pg = int(soup.find_all('label', class_="paginator-label")[1].text.split(" ")[1].split("/")[0])
            else:
                pg = int(soup.find_all('label', class_="paginator-label")[0].text.split(' ')[1].split("/")[0])


            # Avalia o pipe de leitura dos dados
            # Possui detalhamento?
            info_pesquisa = [x.strip() for x in str(soup.find_all('div', id='geral')[0].find_all('p')[1]).split('<br/>')]
            detalhamento_1 = [s for s in info_pesquisa if "First detail" in s]
            detalhamento_2 = [s for s in info_pesquisa if "Second detail" in s]
            qt_periodos = len([s for s in info_pesquisa if "Period" in s])

            #   print "detalhamentos", detalhamento_1, detalhamento_2

            if detalhamento_1 == []:
                print("detalhamento_1 é []")
                # cria a tabela com as 5 colunas dos dados [periodo, US$ FOB, Peso Liquido, Quantidade]
                header_raw = soup.find(class_="gridSubtitle")
                header = ["numero_pagina"]+[x.text for x in header_raw]

                # Extrai as informacoes da tabela
                string = soup.select('tr[id*=consulta_simples_row]')  # Obtem informacao
                dados_tbl = [line for line in string]
                for dados in dados_tbl:
                    output_request.append([pg]+[x.text for x in dados])

            else:
                if detalhamento_2 == []:
                    print("detalhamento_2 é []")
                    # Somente um detalhamento - cria tabela com 6 colunas dos dados [pg, detalhamento_1,periodo, US$ FOB, Peso Liquido, Quantidade]
                    # Header dos dados
                    detalhamento_1 = [s for s in detalhamento_1][0].split(': ')[1]
                    header_raw = soup.find(class_="gridSubtitle")
                    header = ["numero_pagina", detalhamento_1] + [x.text for x in header_raw]

                    # Extrai as informacoes da tabela
                    description_info = soup.find_all(id=None, class_="row-even")    # Obtem informacao dos detalhamentos
                    string = soup.select('tr[id*=consulta_detalhada_row]')          # Obtem informacao
                    detalhamento_1_info = [x.text for x in description_info]
                    dados_tbl = [line for line in string]

                    # Replica a descricao para cada linha do periodo
                    detalhamentos = []
                    for detalhamento in detalhamento_1_info:
                        for i in range(qt_periodos):
                            detalhamentos.append(detalhamento)

                    for dados, detalhamento in zip(dados_tbl, detalhamentos):
                        output_request.append([pg] + [detalhamento] + [x.text for x in dados])

                else:
                    print("entrou no else")
                    # Dois detalhamentos - cria tabela com 7 colunas dos dados [pg, detalhamento_1, detalhamento_2, periodo, US$ FOB, Peso Liquido, Quantidade]
                    # Header dos dados
                    detalhamento_1 = [s for s in detalhamento_1][0].split(': ')[1]
                    detalhamento_2 = [s for s in detalhamento_2][0].split(': ')[1]
                    print(detalhamento_1, detalhamento_2)

                    header_raw = soup.find(class_="gridSubtitle")
                    header = ["numero_pagina", detalhamento_1, detalhamento_2] + [x.text for x in header_raw]
                    # Extrai as informacoes da tabela
                    description_info = soup.find_all(id=None, class_="row-even")    # Obtem informacao dos detalhamentos
                    string = soup.select('tr[id*=consulta_detalhada_row]')          # Obtem informacao das quantidades

                    # Extrai os dados do html
                    # print "description_info", description_info
                    # print [x for x in description_info]
                    detalhamento_1_info = [x for x in description_info][0].text
                    detalhemento_2_info = [x.text for x in description_info][1:]
                    dados_tbl = [line for line in string][qt_periodos+1:]

                    # une as informacoes da tabela
                    detalhamentos = []
                    for detalhamento in detalhemento_2_info:
                        print("detalhamentos - ", detalhamento)
                        for i in range(qt_periodos):
                            detalhamentos.append(detalhamento)
                    print("construiu detalhamentos - ",)
                    for det_2, dados in zip(detalhamentos, dados_tbl):
                        output_request.append([pg, detalhamento_1_info, det_2]+[x.text for x in dados])

                    print("juntou detalhamento dados")
        # Vou deletar os htmls processados para ficar mais leve
        # os.remove(htmls_address+'/'+file)
        # shutil.move(htmls_address+"/"+file, dir_path+"/"+"processed_html"+"/"+file)
    print("compilou todos os arquivos")
    # informcoes para
    nome_arquivo = file_name[0:len(file_name)]

    ga.salva_arquivo_tratado(output_request, header, nome_arquivo, pasta_saida)
    print("salvou arquivo na pasta")


def merge_email(id_req, dir_path):
    # endereco provisorio somente com a finalidade de teste
    # bloco provisório para teste - depois essa query passa a sair do sub_fetch - a 6 e exemplo
    db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_dirpath = os.path.abspath(os.path.join(db_dirpath, ".."))

    with sql.connect(db_dirpath+'/pais_alice_requests.db') as conn:
        result = conn.execute('''select ss.emaill_file_path, ss.emaill_file_name, sc.*
                                from sub_requests_queue_statuses    as ss
                                inner join sub_request_content      as sc on ss.id_sub = sc.id_sub
                                where ss.id_request=?;
                                ''', (str(id_req),))

        email_list_address = result.fetchall()
    print(email_list_address)
    # email_list_headers = headers.fetchall()
    print('--------------------------------------------------------------------------')
    print(dir_path)
    print('--------------------------------------------------------------------------')
    # Inicia a unificacao dos arquivos

    data_arq = []
    n_arquivo = 1
    for file in email_list_address:
        # Constroi o endereco do arquivo
        file_address = file[0]
        file_name = file[1]
        # Obtem a caracterizacao do arquivo
        email_id =file[3]
        sentido_trade = file[7]
        tipo_ncm = file[8]
        modo_ncm = file[9]
        lista_ncm = file[10]
        bloco = file[11]
        pais = file[12]
        uf = file[13]
        porto = file[14]
        via = file[15]
        primeiroDetalhamento = file[16]
        segundoDetalhamento = file[17]
        periodos = [p for p in file[18:24] if p != None]

        # Abre o arquivo
        book = open_workbook(file_address+"/"+file_name, on_demand=True)
        data = []

        # Obtem a linha onde os dados iniciam
        sheet_1 = book.sheet_by_name('Aliceweb_parte_1')
        row_inicio = 0
        while sheet_1.col(1)[0].value == sheet_1.col(1)[row_inicio].value:
            row_inicio = row_inicio + 1
        print("row_inicio ", file_name, row_inicio, len(periodos), periodos)

        # Criar um bloco de codigo para obter a primeira linha
        for name in book.sheet_names():
            sheet = book.sheet_by_name(name)

            if name == 'Aliceweb_parte_1':
                row_header = row_inicio

            else:
                row_header = row_inicio
                row_inicio = -1

            # Dados comecam na coluna 2 * qt_descricoes
            if primeiroDetalhamento == segundoDetalhamento:
                # O unico caso possivel eh ambos sendo None
                qt_detalhamento = 0
            else:
                if segundoDetalhamento == None:
                    qt_detalhamento = 1
                else:
                    qt_detalhamento = 2

            col_inicial = qt_detalhamento*2
            # O numero de colunas de dados 3 * qt_periodos
            qt_dados = 3*len(periodos)

            raw_data = readRows(sheet)
            raw_data_1 = readRows(sheet_1)

            # Inicia obtenção dos dados a partir da linha inicial dos dados
            # Colunas de atributos
            for row in raw_data[row_inicio+1:]:

                row_info = row[0:col_inicial]+[email_id]+[file_name]+[sentido_trade]+[bloco]+[pais]+[uf]+[porto]+[via]
                # print(row_info)
                for periodo in range(len(periodos)):
                    coluna_ref = col_inicial + (3*periodo) + 1
                    # Acrescenta a a data dos dados
                    # Bloco o codigo responsavel por retirar as linhas zeradas
                    soma = row[coluna_ref-1] + row[coluna_ref] + row[coluna_ref+1]

                    if soma == 0:
                        pass
                    else:
                        info = [float(x) for x in row[coluna_ref - 1:coluna_ref + 2]]
                        data.append(row_info + [raw_data_1[row_header-1][coluna_ref-1]] + info)

            # Caso a
            if name == 'Aliceweb_parte_1':
                data_col_name = [x.split(" de ")[0] for x in raw_data[row_inicio][col_inicial:col_inicial + 3]]
                header_row = raw_data[row_inicio][0:col_inicial] + ['email_id','file_name','sentido_trade','bloco','pais','uf','porto','via', 'data'] + data_col_name
            else:
                # Caso eu esteja na aba 2, é necessario buscar as datas na aba 1
                data_col_name = [x.split(" de ")[0] for x in raw_data_1[row_header][col_inicial:col_inicial + 3]]
                header_row = raw_data_1[row_header][0:col_inicial] + ['email_id','file_name','sentido_trade','bloco','pais','uf','porto','via', 'data'] + data_col_name

            data_pd = pd.DataFrame(data, columns=header_row)
            data_arq.append(data_pd)

        n_arquivo += 1

    # Concatena o resultado
    with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
        result = conn.execute('''select ss.req_file_name
                                 from requests_queue_statuses as ss where ss.id=?;''', (id_req,))
        nome_file = result.fetchall()

    # print("concatena dados")
    frame = pd.concat(data_arq)
    frame.to_csv(dir_path+"/reports/"+nome_file[0][0]+".csv", sep=";", decimal=",", encoding='latin-1')

if __name__ == '__main__':
    dir_path = '/usr/lib/cgi-bin/pais_alice/app/reports/20160914_184451_worker_1'
    merge_email(6,dir_path)