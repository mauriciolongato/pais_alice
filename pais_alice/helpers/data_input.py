# -*- coding: latin-1 -*-
import json
import csv
import ast
import re
import datetime


def trata_ncm(ncm_string):
    # print "string_ncm: ", type(ncm_string), ncm_string
    ncm = re.findall(r'\d+', ncm_string)
    # print "imprime ncms tratados: ", ncm
    return ncm

def open_json(nome_arquivo):
    with open(nome_arquivo) as json_data:
        d = json.load(json_data)
        json_data.close()
    return d

def open_input_excel(nome_arquivo):
    request = {}
    with open(nome_arquivo) as f:
        reader = csv.reader(f)
        info_pipe = {}
        info_periodo = {}
        info_ncm = []

        for row in reader:
            if row[0] == 'pipe':
                if row[2] == "Nenhum":
                    info_pipe[row[1]] = ""
                else:
                    if row[1] == 'detalhamento':
                        info_pipe[row[1]] = ast.literal_eval(row[2])
                    else:
                        info_pipe[row[1]] = row[2]

            if row[0] == 'periodo':
                info_periodo[row[1]] = row[2]

            if row[0] == 'ncm':
                info_ncm.append(row[2])
        f.close()

        # request['pipe'] = info_pipe
        # request['ncm'] = ast.literal_eval(info_ncm[0])

        # Funcao retorna em periodos estruturados em blocos de 6 periodos
        periodos_estruturados = estrutura_periodos(info_periodo, info_pipe['periodo'])
        requests = []
        for periodos in periodos_estruturados:
            request = {}

            request['pipe'] = info_pipe
            request['ncm'] = ast.literal_eval(info_ncm[0])
            request['periodo'] = periodos

            requests.append(request)

    return requests

def open_php(request=None):
    if request == None:
        requisicao = {'pipe': {'porto': '4117', 'via': "", 'detalhamento': ['TX_CD_UF', 'TX_CD_PAIS'], 'modo_ncm': 'unitario',
                     'bloco_economico': "", 'senha': '8532vxtp', 'ncm_tipo': 'TX_CD_SH8', 'pais': "",
                     'login': 'mauriciolongato', 'sentido': 'Imp', 'estado': "", 'periodo': 'Mensal'}, 'periodo':
                {'periodo-periodoMesFinal': '04', 'periodo-periodoAnoFinal': '2015',
                 'periodo-periodoAnoInicio': '2015', 'periodo-periodoMesInicio': '01'},
            'ncm': [12019000, 12010090, 12010010, 23040090, 23040010, 10059010, 10051000, 10059090]}
    else:
        #print "request diferente de vazia"
        requisicao = request

    # Estrutura intervalos
    info_pipe = requisicao['pipe']
    info_periodo = requisicao['periodo']
    # print "info_pipe",type(info_pipe), info_pipe
    # print "info_periodo", type(info_periodo), info_periodo

    # Funcao retorna em periodos estruturados em blocos de 6 periodos
    periodos_estruturados = estrutura_periodos(info_periodo, info_pipe['periodo'])
    # print "peridos estruturados: ", periodos_estruturados
    requests = []
    for periodos in periodos_estruturados:
        request = {}
        request['pipe'] = info_pipe
        request['ncm'] = trata_ncm(requisicao['ncm'][0])
        request['periodo'] = periodos

        requests.append(request)

    # print "request tratada: ", requests
    return requests



def estrutura_periodos(periodo, passo):
    # Obtem as datas
    mes_inicio = int(periodo[0]['periodo-periodoMesInicio'])
    ano_inicial = int(periodo[0]['periodo-periodoAnoInicio'])
    mes_final = int(periodo[0]['periodo-periodoMesFinal'])
    ano_final = int(periodo[0]['periodo-periodoAnoFinal'])
    #print "estrut_periodos datas: ", mes_inicio, ano_inicial, " - ", mes_final, ano_final

    # Caso o pedido seja para dados mensais
    if passo == "mensal":
        #print "entrou mensal"
        # Coloca os dados em formato de data
        inicio_periodo = datetime.date(ano_inicial, mes_inicio, 1)
        final_periodo = datetime.date(ano_final, mes_final, 1)
        numdays = final_periodo - inicio_periodo

        # lista os dias no intervalo entre as datas
        date_list = [int((final_periodo - datetime.timedelta(days=x)).strftime('%Y%m')) for x in range(0, numdays.days)]
        # Retira as repeticoes no vetor de datas yyyymm e ordena do mais antigo para o mais novo
        date_list = sorted(list(set(date_list)))

        # Cria os pares para os intervalos mensais
        periodos_mensais = [[inicio, fim] for inicio, fim in zip(date_list, date_list)]
        lista_periodo = [periodos_mensais[i:i + 6] for i in range(0, len(periodos_mensais), 6)]
        # Cria lista com as datas
        periodos_requisicoes = []
        for intervalo in lista_periodo:
            periodos = []
            for i in range(len(intervalo)):
                periodo = {}
                periodo['periodo-periodoMesInicio_'+str(i+1)] = str(intervalo[i][0])[4:]
                periodo['periodo-periodoAnoInicio_'+str(i+1)] = str(intervalo[i][0])[0:4]
                periodo['periodo-periodoMesFinal_'+str(i+1)] = str(intervalo[i][1])[4:]
                periodo['periodo-periodoAnoFinal_'+str(i+1)] = str(intervalo[i][1])[0:4]
                periodos.append(periodo)
            periodos_requisicoes.append(periodos)
        
        #print "periodos", periodos_requisicoes
        return periodos_requisicoes

    if passo == "anual":
        # Coloca os dados em formato de data
        inicio_periodo = datetime.date(ano_inicial, 1, 1)
        final_periodo = datetime.date(ano_final, 12, 1)
        numdays = final_periodo - inicio_periodo

        # lista os dias no intervalo entre as datas
        date_list = [int((final_periodo - datetime.timedelta(days=x)).strftime('%Y')) for x in range(0, numdays.days)]
        # Retira as repeticoes no vetor de datas yyyymm e ordena do mais antigo para o mais novo
        date_list = sorted(list(set(date_list)))

        # Cria os pares para os intervalos mensais
        periodos_mensais = [[inicio, fim] for inicio, fim in zip(date_list, date_list)]
        lista_periodo = [periodos_mensais[i:i + 6] for i in range(0, len(periodos_mensais), 6)]
        print(lista_periodo)
        # Cria lista com as datas
        periodos_requisicoes = []
        for intervalo in lista_periodo:
            periodos = []
            for i in range(len(intervalo)):
                periodo = {}
                periodo['periodo-periodoMesInicio_'+str(i+1)] = "01"
                periodo['periodo-periodoAnoInicio_'+str(i+1)] = str(intervalo[i][0])[0:4]
                periodo['periodo-periodoMesFinal_'+str(i+1)] = "12"
                periodo['periodo-periodoAnoFinal_'+str(i+1)] = str(intervalo[i][1])[0:4]
                periodos.append(periodo)
            periodos_requisicoes.append(periodos)
            # print "#periodos: ", len(periodos)
        # print len(periodos_requisicoes)
        return periodos_requisicoes

    else:
        periodo = {}
        # Caso o usuario peca uma consulta simples entre duas datas ja definidas por ele
        # OBS!!!! ESSA POSSIBILIDADE AINDA NAO ESTA MAPEADA NO EXCEL!!!
        periodo['periodo-periodoMesInicio_1'] = mes_inicio
        periodo['periodo-periodoAnoInicio_1'] = ano_inicial
        periodo['periodo-periodoMesFinal_1'] = mes_final
        periodo['periodo-periodoAnoFinal_1'] = ano_final
        periodos.append(periodo)
        periodos_requisicoes.append(periodos)

        return periodos_requisicoes

def estrutura_ncm():
    exec_lista_ncm = [ncm_list[i:i + 60] for i in range(0, len(ncm_list), 60)]



if __name__ == "__main__":
    input_address = 'C:\\Users\\mauricio.longato\\PycharmProjects\\scrap_antaq\\input_excel_aliceweb\\'
    arquivo = '20160721152138_mauriciolongato.csv'
    requests = open_input_excel(input_address+arquivo)
    print(requests[0])

    base = datetime.datetime.today()
    numdays = 60
    date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]

    pipe_exec = dict(login='mauriciolongato', senha='6908dhph', modo_ncm='unitario', bloco_economico='', pais='',
                     estado='', porto='SANTOS', via='', periodo='unico', detalhamento=['UF', 'NCM 8 dígitos'],
                     sentido='Imp', ncm_tipo='NCM 8 dígitos')

    datas_id = [
        {'periodo-periodoAnoInicio_1': '2015', 'periodo-periodoMesInicio_1': '04', 'periodo-periodoAnoFinal_1': '2016',
         'periodo-periodoMesFinal_1': '05'}]

    ncm_list = ['15010000', '15011000', '15012000', '15019000', '15020011', '15020012', '15020019', '15020090',
                '15021011', '15021012', '15021019', '15021090', '15029000', '15030000', '15041011', '15041019',
                '15041090',
                '15042000', '15043000', '15050010', '15050090', '15051000', '15059010', '15059090', '15060000',
                '15071000',
                '15079010', "15079011", '15079019', '15079090', '15081000', '15089000', '15091000', '15099010',
                '15099090',
                '15100000', '15111000', '15119000', '15121110', '15121120', '15121910', '15121911', '15121919',
                '15121920',
                '15122100',
                '15122910', '15122990', '15131100', '15131900', '15132110', '15132120', '15132910', '15132920',
                '15141000',
                '15141100', '15141910', '15141990', '15149010', '15149090', '15149100', '15149910', '15149990',
                '15151100',
                '15151900', '15152100', '15152900', '15152910', '15152990', '15153000', '15154010', '15154020',
                '15154090',
                '15155000', '15156000', '15159000', '15159010', '15159021', '15159022', '15159090', '15161000',
                '15162000',
                '15171000', '15179000', '15179010', '15179090', '15180000', '15180010', '15180090', '15200010',
                '15200020',
                '15211000', '15219011', '15219019', '15219090', '15220000', '16010000', '16021000', '16022000',
                '16023100',
                '16023200', '16023210', '16023220', '16023230', '16023290', '16023900', '16024100', '16024200',
                '16024900',
                '16025000', '16029000', '16030000', '16041100', '16041200', '16041310', '16041390', '16041410',
                '16041420',
                '16041430', '16041500', '16041600', '16041700', '16041900', '16042010', '16042020', '16042030',
                '16042090',
                '16043000', '16043100', '16043200', '16051000', '16052000', '16052100', '16052900', '16053000',
                '16054000',
                '16055100', '16055200', '16055300', '16055400', '16055500', '16055600', '16055700', '16055800',
                '16055900',
                '16056100', '16056200', '16056300', '16056900', '16059000']

    data = {'pipe': pipe_exec, 'periodo': datas_id, 'ncm': ncm_list}

    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile)
