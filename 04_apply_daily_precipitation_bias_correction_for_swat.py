# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:28:37 2024

@author: LENOVO
"""

import os
import pandas as pd
import numpy as np



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
    
    
    # Ruta del archivo CSV con datos de celda
    csv_file = "D:/Seasonal_forecast/SWAT/subcuencascabeceradeltajohastabolarque/centroide_vs_aemet_vs_ECMWF.csv"
    # Leer el archivo CSV
    df = pd.read_csv(csv_file)
    # Filtrar la fila correspondiente a la subcuenca específica
    subcuenca_data = df[df['Subbasin'] == subcuenca]
    
    # Información de ubicación (estos valores deben ser adaptados según los datos reales)
    nbyr = 2
    tstep = 0
    lat = subcuenca_data['LAT'].values[0]
    lon = subcuenca_data['LONG'].values[0]
    elev = subcuenca_data['Elev'].values[0]
    
    # Llama a la función para leer y procesar el archivo
    coeficientes_correctores = read_and_process_file(subcuenca, mes)
    
    ##############  Para cargar la pcp diaria que hay que corregir 
    
    # Directorio donde se encuentra el archivo CSV
    data_folder = "D:/Seasonal_forecast/Bias_correction_LSTM/Preparar_Datos/Datos_brutos_medios/"
    
    
    # Iterar sobre los años desde 1981 hasta 2019
    for year in range(1981, 2020):
        # Construye el nombre del archivo basado en los parámetros
        filename_pattern = f"pcp_daily_MEAN_subcuenca_{subcuenca}_mes_{mes}_year_{year}"
    
        # Encuentra el nombre del archivo que cumple con el patrón
        matching_file = None
        for filename in os.listdir(data_folder):
            if filename.startswith(filename_pattern):
                matching_file = filename
                break
    
        if matching_file:
            # Lee solo las columnas cero (fecha) y dos (Precipitacion_ECMWF_mean)
            filepath = os.path.join(data_folder, matching_file)
            df_pcp_uncorrected = pd.read_csv(filepath, usecols=[0, 2], header=0)  # Lee solo las columnas necesarias, con la primera fila como encabezado
            # Crea una nueva columna 'Año' extrayendo el año de la fecha en la columna cero
            df_pcp_uncorrected['Año'] = year
            # Agregar una nueva columna 'monthly' que representa el número de mes 
            df_pcp_uncorrected['monthly'] = pd.to_datetime(df_pcp_uncorrected.iloc[:, 0]).dt.month
            # Crear una nueva columna 'lead_time_monthly'
            # Obtener los valores únicos en el orden de aparición
            unique_months_in_order = pd.unique(df_pcp_uncorrected['monthly'])
            # Crear un diccionario para mapear cada mes a su lead time
            month_to_lead_time = {month: i + 1 for i, month in enumerate(unique_months_in_order)}
            # Mapear los valores en la columna 'monthly' a 'lead_time_monthly'
            df_pcp_uncorrected['lead_time_monthly'] = df_pcp_uncorrected['monthly'].map(month_to_lead_time)
            # Eliminar las filas donde el lead_time sea 8
            df_pcp_uncorrected = df_pcp_uncorrected[df_pcp_uncorrected['lead_time_monthly'] != 8]
    
            # Crear una nueva columna en df_pcp_uncorrected para almacenar el coeficiente corrector
            df_pcp_uncorrected['Coeficiente_Corrector'] = 1
    
            # Iterar sobre cada fila en df_pcp_uncorrected
            for index, row in df_pcp_uncorrected.iterrows():
                # Obtener el año y el lead_time_monthly para esta fila
                año = row['Año']
                lead_time_monthly = row['lead_time_monthly']
                
                # Verificar si el año existe en coeficientes_correctores
                if año in coeficientes_correctores.index:
                    # Obtener el coeficiente corrector correspondiente al año y lead_time_monthly
                    coeficiente = coeficientes_correctores.at[año, f'leadtime_{lead_time_monthly}']
                    # Asignar el coeficiente corrector a la nueva columna en df_pcp_uncorrected
                    df_pcp_uncorrected.at[index, 'Coeficiente_Corrector'] = coeficiente
    
            # Multiplicar la precipitación por el coeficiente corrector y almacenarla en la nueva columna 'Precipitacion_Corregida'
            df_pcp_uncorrected['Precipitacion_Corregida'] = df_pcp_uncorrected['Precipitacion_ECMWF_mean'] * df_pcp_uncorrected['Coeficiente_Corrector']
    
            #  Obtener la fecha del primer dato en df_pcp_uncorrected
            fecha_primer_dato = pd.to_datetime(df_pcp_uncorrected.iloc[0, 0])        
            # Crear fechas para el año completo previo hasta el día antes de la fecha_primer_dato
            start_prev_year = pd.Timestamp(f"{fecha_primer_dato.year - 1}-01-01")
            end_prev_day = fecha_primer_dato - pd.Timedelta(days=1)
            fechas_previas = pd.date_range(start=start_prev_year, end=end_prev_day, freq='D')
    
            ###################################################
            # Directorios de los archivos
            csv_file = r'D:\Seasonal_forecast\SWAT\subcuencascabeceradeltajohastabolarque\centroide_vs_aemet_vs_ECMWF.csv'
            pcp_AEMET_dir = r'D:\AEMET_V2\1951-2022\pcp\pcp_AEMET_1951-2022'
            # Leer el archivo CSV
            data = pd.read_csv(csv_file, usecols=['ID', 'celda', 'Subbasin'])
            # Renombrar las columnas
            data.rename(columns={'ID': 'AEMET_Celda', 'celda': 'ECMWF_Celda', 'Subbasin': 'Subcuenca'}, inplace=True)
            # Definir rango de años
            # Filtrar los datos por subcuenca
            subcuenca_data = data[data['Subcuenca'] == subcuenca]
            # Obtener el nombre de la celda de AEMET y ECMWF
            aemet_celda = subcuenca_data['AEMET_Celda'].iloc[0]
            # Leer datos de precipitación AEMET
            pcp_AEMET_file = os.path.join(pcp_AEMET_dir, f'{aemet_celda}_PCP.txt')
            pcp_AEMET_data = np.loadtxt(pcp_AEMET_file, skiprows=1)  # Saltar la primera fila 
            # Definir fechas desde el 1/1/1951 hasta la longitud de los datos
            start_date = '1951-01-01'
            end_date = pd.Timestamp(start_date) + pd.Timedelta(days=len(pcp_AEMET_data)-1)
            dates = pd.date_range(start=start_date, end=end_date, freq='D') 
            # Crear DataFrames con fechas como índice
            pcp_AEMET_df = pd.DataFrame(pcp_AEMET_data, index=dates, columns=['Precipitacion'])
    
            
            # Extraer los valores correspondientes a las fechas previas
            pcp_prev_year = pcp_AEMET_df.loc[fechas_previas]
            # Convertir los datos a una serie de valores
            pcp_prev_year_series = pcp_prev_year['Precipitacion'].values
    
            # Crear el DataFrame
            pcp_prev = pd.DataFrame({'Unnamed: 0': fechas_previas, 'Precipitacion_Corregida': pcp_prev_year_series})
            # Cambiar el formato de la columna de fecha
            pcp_prev['Unnamed: 0'] = pcp_prev['Unnamed: 0'].dt.strftime('%Y-%m-%d')
            
           
            # Concatenar el DataFrame de datos aleatorios con df_pcp_uncorrected
            df_pcp_uncorrected_extended = pd.concat([pcp_prev, df_pcp_uncorrected], ignore_index=True)
           
            output_folder_1 = "D:/Seasonal_forecast/Bias_corrected_forecast_monthly/clima_diario_corregido_para_SWAT"
            # Nombre del mes en texto
            nombre_mes = mes        
            # Ruta de la carpeta correspondiente al año y al mes
            output_folder_mes = os.path.join(output_folder_1, f"{nombre_mes}_{year}")
            # Crear la carpeta si no existe
            os.makedirs(output_folder_mes, exist_ok=True)
            # Crear la carpeta "pcp" dentro de la carpeta del mes y año
            carpeta_pcp = os.path.join(output_folder_mes, "pcp")
            os.makedirs(carpeta_pcp, exist_ok=True)      
            
            
            # Nombre del archivo
            output_filename = f"Corrected_pcp_subcuenca_{subcuenca}.pcp"
            # Ruta completa del archivo de salida
            output_filepath = os.path.join(carpeta_pcp, output_filename)
                   
          
            # Suponiendo que 'Unnamed: 0' es el nombre de la columna que contiene las fechas
            # Reemplaza 'Unnamed: 0' con el nombre real de la columna si es diferente
            df_pcp_uncorrected_extended['Unnamed: 0'] = pd.to_datetime(df_pcp_uncorrected_extended['Unnamed: 0'])
            
            # Extraer el año y el día del año
            df_pcp_uncorrected_extended['Año'] = df_pcp_uncorrected_extended['Unnamed: 0'].dt.year
            df_pcp_uncorrected_extended['Dia_del_Año'] = df_pcp_uncorrected_extended['Unnamed: 0'].dt.dayofyear
            
            # Abrir el archivo en modo de escritura
            with open(output_filepath, 'w') as f:
                # Escribir la cabecera del archivo
                f.write(f"{output_filename}: Precipitation data - file written by SWAT+ editor {pd.Timestamp.now()}\n")
                f.write("nbyr     tstep       lat       lon      elev\n")
                f.write(f"{nbyr:<8}{tstep:<10}{lat:<10}{lon:<10}{elev:<10}\n")
                
                # Escribir los datos de precipitación
                for index, row in df_pcp_uncorrected_extended.iterrows():
                    # Obtener la fecha del DataFrame utilizando el índice
                    fecha = df_pcp_uncorrected_extended.iloc[index]['Unnamed: 0']
                    # Obtener el año, el día del año y el valor de la precipitación
                    año = fecha.year
                    dia_del_ano = fecha.timetuple().tm_yday
                    pcp_value = row['Precipitacion_Corregida']
                    # Escribir los datos en el archivo
                    f.write(f"{año:<8}{dia_del_ano:<8}{pcp_value:<10.5f}\n")
    
            # Asegúrate de que el bloque 'with open' se ha cerrado antes de imprimir el mensaje de archivo guardado.
            print(f"Archivo guardado como '{output_filepath}'")
