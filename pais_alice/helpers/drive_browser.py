# -*- coding: latin-1 -*-
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
import time



def exec_login(driver, pipe_exec):
    # Processo de login
    # login
    name_element = driver.find_element_by_id('logUser')
    att = pipe_exec['login']
    name_element.send_keys(att)
    # senha
    name_element = driver.find_element_by_id('logPass')
    att = pipe_exec['senha']
    name_element.send_keys(att)
    # Clica no botao
    driver.find_element_by_id('btnLogin').click()

def exec_define_pesquisa(driver, pipe_exec):
    if pipe_exec['sentido'] == 'Exp':
        second_link = 'http://aliceweb.mdic.gov.br//consulta-ncm/index/type/exportacaoNcm'
        driver.get(second_link);
    if pipe_exec['sentido'] == 'Imp':
        second_link = 'http://aliceweb.mdic.gov.br//consulta-ncm/index/type/importacaoNcm'
        driver.get(second_link);

def exec_insere_nmc(driver, list_ncm, pipe_exec):
    ''' driver      - corresponde ao controle do browser para a funcao
        list_ncm    - ja contem os ncm no formato adequado para cada uma das opcoes:
                        1. se unitario, a lista insere um a um ate o limite de 60
                        2. se intervalo, a lista deve conter somente 2 itens
        pipe_exec   - contem as informacoes que definem o pipe da execucao da extracao
    '''

    if pipe_exec['modo_ncm'] == 'unitario':
        # Insere os NMCs
        driver.find_element_by_id('btnCesta').click()
        time.sleep(0.5)
        for ncm in list_ncm:
            ncm_element_final = driver.find_element_by_id("valorNcmCesta")
            ncm_element_final.send_keys(ncm)
            ncm_element_final.send_keys(Keys.ENTER)
            driver.find_element_by_id('btnAddProduto').click()
            # time.sleep(1)

    if pipe_exec['modo_ncm'] == 'intervalo':
        # Escolhe a modalidade de codigo de busca - padrao atual, ncm-8
        options_detalhamento = driver.find_element_by_id('tipoNcm')
        options = options_detalhamento.find_elements_by_tag_name('option')
        detalhamento_ref = pipe_exec['ncm_tipo']
        [option.click() if option.get_attribute('value') == detalhamento_ref else '' for option in options]
        time.sleep(1)

        # Insere os valores
        ncm_inicial = list_ncm[0]
        ncm_final = list_ncm[1]
        print("NCMs: ", ncm_inicial, ncm_final)
        # ncm inicial
        ncm_element_inicial = driver.find_element_by_id("valorNcmInicial")
        ncm_element_inicial.send_keys(ncm_inicial)
        ncm_element_inicial.send_keys(Keys.ENTER)
        time.sleep(0.8)
        # ncm final
        ncm_element_final = driver.find_element_by_id("valorNcmFinal")
        ncm_element_final.send_keys(ncm_final)
        ## time.sleep(0.5)
        ncm_element_final.send_keys(Keys.ENTER)
        time.sleep(0.5)
        driver.find_element_by_id("primeiroDetalhamento").click()
        time.sleep(0.5)

def exec_insere_bloco_economico(driver, pipe_exec):
    if pipe_exec['bloco_economico'] == '':
        pass
    else:
        ncm_element_final = driver.find_element_by_id("bloco")
        [x.click() if x.get_attribute('value') == pipe_exec['bloco_economico'] else '' for x in
         ncm_element_final.find_elements_by_tag_name("option")]
        time.sleep(0.5)

def exec_insere_pais(driver, pipe_exec):
    if pipe_exec['pais'] == '':
        pass
    else:
        ncm_element_final = driver.find_element_by_id("pais")
        [x.click() if x.get_attribute('value') == pipe_exec['pais'] else '' for x in
         ncm_element_final.find_elements_by_tag_name("option")]
        time.sleep(0.5)

def exec_insere_estado(driver, pipe_exec):
    if pipe_exec['estado'] == '':
        pass
    else:
        ncm_element_final = driver.find_element_by_id("uf")
        [x.click() if x.get_attribute('value') == pipe_exec['estado'] else '' for x in
         ncm_element_final.find_elements_by_tag_name("option")]
        time.sleep(0.5)

def exec_insere_porto(driver, pipe_exec):
    if pipe_exec['porto'] == '':
        pass
    else:
        ncm_element_final = driver.find_element_by_id("porto")
        [x.click() if x.get_attribute('value') == pipe_exec['porto'] else '' for x in ncm_element_final.find_elements_by_tag_name("option")]
        ## time.sleep(0.5)

def exec_insere_vias(driver, pipe_exec):
    if pipe_exec['via'] == '':
        pass
    else:
        ncm_element_final = driver.find_element_by_id("via")
        [x.click() if x.get_attribute('value') == pipe_exec['via'] else '' for x in
         ncm_element_final.find_elements_by_tag_name("option")]
        time.sleep(0.5)

def exec_insere_detalhamentos(driver, pipe_exec):
    if pipe_exec['detalhamento'] == '':
        pass

    if len(pipe_exec['detalhamento']) == 1:
        options_detalhamento = driver.find_element_by_id('primeiroDetalhamento')
        options = options_detalhamento.find_elements_by_tag_name('option')
        detalhamento_ref = pipe_exec['detalhamento'][0]
        [option.click() if option.get_attribute('value') == detalhamento_ref else '' for option in options]
        time.sleep(0.5)

    if len(pipe_exec['detalhamento']) == 2:
        print("possui 2 detalhamentos")
        # Primeiro detalhamento
        # options_detalhamento = driver.find_element_by_id('primeiroDetalhamento')
        # options = options_detalhamento.find_elements_by_tag_name('option')
        # detalhamento_ref = pipe_exec['detalhamento'][0]
        # driver.find_element_by_id("primeiroDetalhamento").click()
        ncm_element_final = driver.find_element_by_id("primeiroDetalhamento")
        [x.click() if x.get_attribute('value') == pipe_exec['detalhamento'][0] else '' for x in
         ncm_element_final.find_elements_by_tag_name("option")]
        time.sleep(0.5)

        # print "1. ",detalhamento_ref
 	# [x.click() if x.get_attribute('value') == detalhamento_ref else '' for x in options]
        # time.sleep(1)

        # Segundo detalhamento
        ncm_element_final = driver.find_element_by_id("segundoDetalhamento")
        [x.click() if x.get_attribute('value') == pipe_exec['detalhamento'][1] else '' for x in
         ncm_element_final.find_elements_by_tag_name("option")]
        time.sleep(0.5)

	# options_detalhamento = driver.find_element_by_id('segundoDetalhamento')
        # options = options_detalhamento.find_elements_by_tag_name('option')
        # detalhamento_ref = pipe_exec['detalhamento'][1]
        # options_text = [''.join(''.join(option.text.split('  ')).split('\n')) for option in options]
        # print "2. ", detalhamento_ref
	# [x.click() if x.get_attribute('value') == detalhamento_ref else '' for x in options]
        # time.sleep(1)

def exec_insere_periodos(driver, periodos, pipe_exec):
    if pipe_exec['periodo'] == '':
        pass

    else: # if pipe_exec['periodo'] == 'multiplo':
        # Acrescenta os intervalos
        # print "check se a quantida de periodos esta correta", len(periodos)
        for i in range(len(periodos)-1):
            time.sleep(2)
            try:
                driver.find_element_by_id('btnAddPeriodo').click()
                time.sleep(1)
            except:
                print("2 segundos nao foram o suficiente")
                time.sleep(2)
                driver.find_element_by_id('btnAddPeriodo').click()

        # Adiciona os intervalos
        for periodo, n_chave in zip(periodos, range(len(periodos))):
            chaves = ['periodo-periodoAnoInicio_{}'.format(n_chave+1), 'periodo-periodoMesInicio_{}'.format(n_chave+1)
                , 'periodo-periodoAnoFinal_{}'.format(n_chave+1), 'periodo-periodoMesFinal_{}'.format(n_chave+1)]
            for chave in chaves:
                op_ano = driver.find_element_by_id(chave)
                options_ano_i = op_ano.find_elements_by_tag_name('option')
                data_ref = periodo[chave]
                [option.click() if option.text == data_ref else '' for option in options_ano_i]
                time.sleep(1)
