# -*- coding: latin-1 -*-
import bs4
import csv
import pandas as pd


def salva_header(html, nome_arquivo, pasta_saida):
    # parseia o arquivo com pandas
    soup = bs4.BeautifulSoup(html, "lxml")
    # Obtem a parte do html com o header
    header = [x.contents for x in soup.find_all('p')][len([x.text for x in soup.find_all('p')]) - 1:][0]

    # Como cara elemento do html tem classes diferentes, devemos trata-los diferentemente
    header_search = []
    for tag in header:
        if str(type(tag)) == "<class 'bs4.element.NavigableString'>":
            tag_text = tag
        else:
            tag_text = tag.text
        header_search.append(tag_text)

    # Retiramos elementos do vetor que ao "pedir" o .text do elemento, foi retornado ""
    header_search = [x for x in header_search if x != ""]
    # posicoes pares do vetor, contem os tags da informacao: ncm, Periodo P1, ets
    colunas = [info.replace(": ", "").replace(":", "") for (info, classe) in
               zip(header_search, range(len(header_search))) if classe % 2 == 0 and info != '']
    # posicoes impares do vetor contem a informacao em si
    valores = [info.replace(": ", "") for (info, classe) in zip(header_search, range(len(header_search))) if
               classe % 2 == 1 and info != '']
    # Cria um dicionario com as informacoes
    tabela = dict(zip(colunas, valores))


    # Salva um csv contendo essas informacoes
    with open(pasta_saida+"/"+nome_arquivo[0:len(nome_arquivo)] + "_header.csv", 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=":", lineterminator='\n')
        for key in sorted(tabela.keys()):
            writer.writerow((key.encode('latin-1'), tabela[key].encode('latin-1')))

def salva_arquivo_tratado(output_request, header, nome_arquivo, pasta_saida):
    # informcoes para pandas
    titulo_row = header
    aliceweb_data_request = pd.DataFrame.from_records(data=output_request, columns=titulo_row)

    # Salva csv
    aliceweb_data_request.to_csv(pasta_saida +'/'+ nome_arquivo + "_tratado.csv", sep=';', encoding='latin-1')
