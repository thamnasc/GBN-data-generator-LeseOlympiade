import pandas as pd
import os
import fnmatch
import re
import docx2txt

directory = "./DateienLeseOlympiade"

file_list= []
for file in os.listdir(directory):
    file_id = int(file.split("_")[0])
    if file_id not in file_list:
        file_list.append(file_id)
file_list.sort()

fill_id = [i for i in range(0,len(file_list))]
fill_columns = ["" for i in range(0,len(file_list))]

df_pergunta = pd.DataFrame(columns=["id", "pagina_id", "pergunta"])
df_pergunta["id"] = fill_id
df_pergunta["pagina_id"] = fill_id
df_pergunta.set_index("id", inplace = True)

df_texto_ocr = pd.DataFrame(columns=["id", "pagina_id", "texto_ocr", "gabarito_ocr", "lingua"])
df_texto_ocr["id"] = fill_id
df_texto_ocr["pagina_id"] = fill_id 
df_texto_ocr.set_index("id", inplace = True)

df_pagina = pd.DataFrame(columns=["id", "pagina_index", "image_path", "exemplar_id"])
df_pagina["id"] = fill_id
df_pagina["pagina_index"] = 0
df_pagina["exemplar_id"] = 0
df_pagina.set_index("id", inplace = True)

pergunta_id = []
pagina_id = []
alternativa = []
alternativa_correta = []

for file in os.listdir(directory):
    file_number = file_list.index(int(file.split("_")[0]))
    if fnmatch.fnmatch(file, '*desafio*') or fnmatch.fnmatch(file, '*gabarito*'):
        file_content = open(directory+"/"+file, "r")
        ocr = file_content.readlines()
        ocr_string = ""
        for line in ocr:
            if line != "\n":
                ocr_string += " "+line.replace("\ufeff", "").rstrip().lstrip()
        ocr_string = re.sub(" ", "", ocr_string, 1) # retira o espaço que está sendo criado no primeiro index da string

        if fnmatch.fnmatch(file, '*desafio*'):
            df_texto_ocr.loc[file_number, 'texto_ocr'] = ocr_string
        else:
            df_texto_ocr.loc[file_number, 'gabarito_ocr'] = ocr_string

    elif fnmatch.fnmatch(file, '*imagem*'):
        lingua = file.split("_")[-1].split(".")[0]
        df_texto_ocr.loc[file_number, 'lingua'] = lingua
        image_path = file.split(".")[0]
        df_pagina.loc[file_number, 'image_path'] = image_path

    elif fnmatch.fnmatch(file, '*resposta*'):
        if file.endswith("docx"):
            file_content = docx2txt.process(directory+"/"+file).split("\n")
            content_lines = []
            for line in file_content:
                if line != "":
                    content_lines.append(line)
            pergunta = content_lines[0]
            respostas = content_lines[1:]

        else:
            file_content = open(directory+"/"+file, "r")
            lines = file_content.readlines()
            formatted_lines = []
            for line in lines:
                formatted_line = line.replace("\ufeff", "").replace("\u200b", "").rstrip().lstrip()
                if formatted_line != "":
                    formatted_lines.append(formatted_line)
            pergunta = formatted_lines[0]
            respostas = formatted_lines[1:]
        
        df_pergunta.loc[file_number, 'pergunta'] = pergunta

        for resposta in respostas:
            formatted_resposta = resposta.split(") ")
            pergunta_id.append(file_number)
            pagina_id.append(file_number)
            alternativa.append(formatted_resposta[-1])
            if "x" in formatted_resposta[0] or "X" in formatted_resposta[0]:
                alternativa_correta.append(True)
            else:
                alternativa_correta.append(False)

df_alternativa = pd.DataFrame(columns=["pergunta_id", "pagina_id", "alternativa", "alternativa_correta"])
df_alternativa["pergunta_id"] = pergunta_id
df_alternativa["pagina_id"] = pagina_id
df_alternativa["alternativa"] = alternativa
df_alternativa["alternativa_correta"] = alternativa_correta
df_alternativa.index.names = ["id"]

df_alternativa = df_alternativa.convert_dtypes()
df_pagina = df_pagina.convert_dtypes()
df_pergunta = df_pergunta.convert_dtypes()
df_texto_ocr = df_texto_ocr.convert_dtypes()

df_alternativa.to_csv("alternativa.csv", sep=";")
df_pagina.to_csv("pagina.csv", sep=";")
df_pergunta.to_csv("pergunta.csv", sep=";")
df_texto_ocr.to_csv("texto_ocr.csv", sep=";")