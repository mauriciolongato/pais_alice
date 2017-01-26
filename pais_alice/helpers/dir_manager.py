# -*- coding: latin-1 -*-
from os import listdir
from os.path import isfile, join, exists
import os


# Recebe os parametros e cria a arvore de pastas
def create_dir(name_request, dir_path):
	request_dir = dir_path+"/"+name_request

	if not os.path.exists(request_dir):
	# Cria pasta que contera os resultados da request
		os.makedirs(request_dir)
		#os.chmod(request_dir, 0777)
		# Cria estrutura de pastas - html
		#os.makedirs(request_dir+"/"+"html")
		#os.makedirs(request_dir+"/"+"processed_html")
		os.makedirs(request_dir+"/"+"reports")
		os.makedirs(request_dir+"/"+"screen_img")
		#os.makedirs(request_dir+"/"+"temp")
		#os.makedirs(request_dir+"/"+"processed_request")

		return request_dir

	else:
		# muda permissoes
		#os.chmod(request_dir, 0777)
		#os.chmod(request_dir+"/"+"html", 0777)
		#os.chmod(request_dir+"/"+"processed_html", 0777)
		#os.chmod(request_dir+"/"+"reports")
		#os.chmod(request_dir+"/"+"screen_img", 0777)
		#os.chmod(request_dir+"/"+"temp")
		#os.chmod(request_dir+"/"+"processed_request", 0777)
		
		return request_dir
