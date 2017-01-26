#! /usr/bin/python
# -*- coding: latin-1 -*-
import os
import sqlite3 as sql
import time
from pyunpack import Archive
from os import listdir
from os.path import isfile, join


# Checar se existe arquivo com zip_status 0
db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
    procs_query = conn.execute('''select * from download_inventory where unzip_status = 0;''')
    procs = procs_query.fetchall()

# Caso exista, deszipar e atualizar o status da tabela
if procs != []:
    ziped_address = os.path.dirname(os.path.realpath(__file__)) + '/attachments'
    unziped_address = os.path.dirname(os.path.realpath(__file__)) + '/unziped_attachments'
    for file_name in procs:
        try:
            file = file_name[1]
            id = file_name[0]
            # Cria pasta de saida
            os.mkdir(unziped_address+"/"+file[:len(file)-4])
            # Extrai para pasta que queremos
            Archive(ziped_address+"/"+file).extractall(unziped_address+"/"+file[:len(file)-4])
            # Obtem o nome do arquivo extraido
            unzipped_file_name = [f for f in listdir(unziped_address+"/"+file[:len(file)-4]) if isfile(join(unziped_address+"/"+file[:len(file)-4], f))]

            # Caso tenha unziped - atualiza o status na tabela
            #conn = sql.connect('/usr/lib/cgi-bin/email_app/alice_email_manager/email_tracker.db')
            db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                conn.execute("update download_inventory set unzip_status=? where email_id=?", (1, id))
                conn.execute("update download_inventory set data_unzip=? where email_id=?", (str(time.strftime("%d/%m/%Y %H:%M:%S")), id))
                conn.execute("update download_inventory set unzipped_file_name=? where email_id=?", (unzipped_file_name[0], id))
                conn.commit()

        except:
            #conn = sql.connect('/usr/lib/cgi-bin/email_app/alice_email_manager/email_tracker.db')
            db_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            with sql.connect(db_dirpath + '/pais_alice_requests.db') as conn:
                conn.execute("update download_inventory set unzip_status=? where email_id=?", (3, id))
                conn.execute("update download_inventory set data_unzip=? where email_id=?",(str(time.strftime("%d/%m/%Y %H:%M:%S")), id))
                conn.commit()
