# -*- coding: utf-8 -*-
"""
Created on Tue May 21 13:54:19 2024

@author: LENOVO
"""

import os
import pandas as pd


####  Para cargar los coeficientes predictores predichos

def read_and_process_file(subcuenca, mes):
    # Define el nombre del archivo basado en subcuenca y mes
    filename = f'coef_correction_pcp_monthly_subcuenca_{subcuenca}_mes_{mes}.csv'
    filepath = os.path.join('D:\\Seasonal_forecast\\Bias_correction_LSTM\\Resultados', filename)

    # Verifica si el archivo existe
    if not os.path.exists(filepath):
        print(f"El archivo {filepath} no existe.")
        return None

    # Lee el archivo CSV en un DataFrame llamado coeficientes_correctores
    coeficientes_correctores = pd.read_csv(filepath, index_col=0)

    # Procesa los datos (aquí simplemente imprimimos el DataFrame)
    print(f"Datos del archivo {filename}:")
    print(coeficientes_correctores)

    # Retorna el DataFrame para que se pueda utilizar fuera de la función
    return coeficientes_correctores

# Especifica el mes y la subcuenca

for subcuenca in range(1, 41):
    print(subcuenca)
    mes = 12
    print(mes)
    
    
    # Llama a la función para leer y procesar el archivo
    coeficientes_correctores = read_and_process_file(subcuenca, mes)
    
    
    ##############  Para cargar la pcp mensual que hay que corregir 
    
    # Directorio donde se encuentra el archivo CSV
    data_folder = "D:/Seasonal_forecast/Bias_correction_LSTM/Predicciones_medias_mensuales"
    
    # Construye el nombre del archivo basado en los parámetros
    filename_pattern = f"Pcp_monthly_mean_ECMWF_subcuenca_{subcuenca}_mes_{mes}_"
    
    # Encuentra el nombre del archivo que cumple con el patrón
    matching_file = None
    for filename in os.listdir(data_folder):
        if filename.startswith(filename_pattern):
            matching_file = filename
            break
    
    if matching_file:
        # Lee el archivo y guarda el contenido como DataFrame
        filepath = os.path.join(data_folder, matching_file)
        df_X = pd.read_csv(filepath)  # Asume que el archivo CSV tiene encabezados y está separado por comas
        # Si deseas guardar el DataFrame en un archivo CSV, puedes hacerlo así:
        # combined_df.to_csv("combined_data.csv", index=False)  # Esto guarda el DataFrame sin incluir el índice en el archivo CSV
    else:
        print("No se encontró ningún archivo que cumpla con el patrón especificado.")
    
    # Modificar los nombres de los índices
    df_X.index = [f"leadtime_{i}" for i in range(1, len(df_X) + 1)]
    
    # Transponer el DataFrame
    df_pcp_uncorrected = df_X.transpose()
    
    
    #####################################################
    ###############  COrreccion de las pcp ###############
    
    # Reindexar los dataframes para asegurar que tienen los mismos índices y columnas
    coeficientes_correctores = coeficientes_correctores.set_index(df_pcp_uncorrected.index)
    coeficientes_correctores.columns = df_pcp_uncorrected.columns
    
    # Multiplica los dataframes elemento a elemento
    pcp_corregida = df_pcp_uncorrected.mul(coeficientes_correctores)
    
    # Formatea el nombre del archivo
    nombre_archivo = f"Corrected_Pcp_monthly_mean_ECMWF_subcuenca_{subcuenca}_mes_{mes}.csv"
    
    # Define la ruta completa del archivo
    ruta = r"D:\Seasonal_forecast\Bias_corrected_forecast_monthly\pcp_mensuales_corregidas"
    ruta_completa = f"{ruta}\\{nombre_archivo}"
    
    # Guarda el resultado en un archivo CSV
    pcp_corregida.to_csv(ruta_completa, index=True)
    
    
    ##############  Para cargar la pcp mensual observada para calcular bias 
    
    # Directorio donde se encuentra el archivo CSV
    data_folder = "D:/Seasonal_forecast/Bias_correction_LSTM/AEMET_mensual"
    
    # Construye el nombre del archivo basado en los parámetros
    filename_pattern = f"Pcp_monthly_AEMET_subcuenca_{subcuenca}_mes_{mes}_"
    
    # Encuentra el nombre del archivo que cumple con el patrón
    matching_file = None
    for filename in os.listdir(data_folder):
        if filename.startswith(filename_pattern):
            matching_file = filename
            break
    
    if matching_file:
        # Lee el archivo y guarda el contenido como DataFrame
        filepath = os.path.join(data_folder, matching_file)
        df_X = pd.read_csv(filepath)  # Asume que el archivo CSV tiene encabezados y está separado por comas
        # Si deseas guardar el DataFrame en un archivo CSV, puedes hacerlo así:
        # combined_df.to_csv("combined_data.csv", index=False)  # Esto guarda el DataFrame sin incluir el índice en el archivo CSV
    else:
        print("No se encontró ningún archivo que cumpla con el patrón especificado.")
    
    # Modificar los nombres de los índices
    df_X.index = [f"leadtime_{i}" for i in range(1, len(df_X) + 1)]
    
    # Transponer el DataFrame
    pcp_obs = df_X.transpose()
    
    ################# Cargar bias original 
    #############################################
    
    # Directorio donde se encuentra el archivo CSV
    data_folder = "D:/Seasonal_forecast/Bias_raw_forecast_monthly/mean"
    
    # Construye el nombre del archivo basado en los parámetros
    filename_pattern = f"raw_biasMult_MEAN_pcp_monthly_subcuenca_{subcuenca}_mes_{mes}_"
    
    # Encuentra el nombre del archivo que cumple con el patrón
    matching_file = None
    for filename in os.listdir(data_folder):
        if filename.startswith(filename_pattern):
            matching_file = filename
            break
    
    if matching_file:
        # Lee el archivo y guarda el contenido como DataFrame
        filepath = os.path.join(data_folder, matching_file)
        bias_obs = pd.read_csv(filepath,header=None)  # Asume que el archivo CSV tiene encabezados y está separado por comas
        # Si deseas guardar el DataFrame en un archivo CSV, puedes hacerlo así:
        # combined_df.to_csv("combined_data.csv", index=False)  # Esto guarda el DataFrame sin incluir el índice en el archivo CSV
    else:
        print("No se encontró ningún archivo que cumpla con el patrón especificado.")
    
    # Modificar los nombres de los índices
    bias_obs.index = [f"leadtime_{i}" for i in range(1, len(df_X) + 1)]
    
    
    ################ Calcular el bias 
    ############################################
    
    # Calcular la media de cada columna en cada DataFrame
    media_pcp_corregida = pcp_corregida.mean()
    media_pcp_obs = pcp_obs.mean()
    
    # Realizar la división de la media de cada columna de pcp_corregida por la media de cada columna de pcp_obs
    biasMult = media_pcp_corregida / media_pcp_obs
    
    # Mostrar los resultados
    print("División de la media de cada columna de pcp_corregida por la media de cada columna de pcp_obs:")
    print(biasMult)
    
    
    #### Comparar bias corregido vs bias original
    
    # Restar 1 a cada valor en el DataFrame bias_obs
    diff_bias_obs = bias_obs - 1
    
    # Restar 1 a cada valor en la serie biasMult
    diff_biasMult = biasMult - 1
    
    # Calcular el valor absoluto de bias_obs y biasMult
    abs_bias_obs = abs(diff_bias_obs[0])
    abs_biasMult = abs(diff_biasMult)
    
    # Comparar los valores absolutos y etiquetar cada fila
    etiqueta_mult = []
    for idx in range(len(abs_bias_obs)):
        if abs_bias_obs[idx] > abs_biasMult[idx]:
            etiqueta_mult.append("Bias reducido")
        else:
            etiqueta_mult.append("Bias aumentado")
    
    # Agregar la etiqueta al DataFrame biasMult
    biasMult = biasMult.to_frame()
    biasMult.columns = ['biasMult']
    biasMult['Etiqueta'] = etiqueta_mult
    
    # Mostrar los resultados
    print(biasMult)
    
    # Definir el nombre del archivo
    nombre_archivo = f"corrected_biasMult_MEAN_pcp_monthly_subcuenca_{subcuenca}_mes_{mes}.csv"
    
    
    # Definir la ruta completa del archivo
    ruta_archivo = r"D:\Seasonal_forecast\Bias_corrected_forecast_monthly\\" + nombre_archivo
    
    # Guardar la serie division_medias como un archivo CSV
    biasMult.to_csv(ruta_archivo, header=True)
    
    print(f"Archivo guardado como {nombre_archivo}")
    
