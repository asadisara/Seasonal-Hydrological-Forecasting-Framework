# -*- coding: utf-8 -*-
"""
Created on Wed May  8 14:54:27 2024

@author: LENOVO
"""

import os
import pandas as pd
import numpy as np

# Directorios de los archivos
csv_file = r'D:\Seasonal_forecast\SWAT\subcuencascabeceradeltajohastabolarque\centroide_vs_aemet_vs_ECMWF.csv'
pcp_AEMET_dir = r'D:\AEMET_V2\1951-2022\pcp\pcp_AEMET_1951-2022'
tmp_AEMET_dir = r'D:\AEMET_V2\1951-2022\tmp\tmp_AEMET_1951-2022'

# Leer el archivo CSV
data = pd.read_csv(csv_file, usecols=['ID', 'celda', 'Subbasin'])
# Renombrar las columnas
data.rename(columns={'ID': 'AEMET_Celda', 'celda': 'ECMWF_Celda', 'Subbasin': 'Subcuenca'}, inplace=True)

# Directorios de los archivos de ECMWF
tp_dir = r'D:\Seasonal_forecast\ECMWF_seasonalForecast\Datos_tp'
t2m_min_dir = r'D:\Seasonal_forecast\ECMWF_seasonalForecast\Datos_t2m_min'
t2m_max_dir = r'D:\Seasonal_forecast\ECMWF_seasonalForecast\Datos_t2m_max'

# Definir rango de años
years = range(1981, 2020)

# Definir nombres de los meses
meses = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']


# Iterar sobre cada subcuenca
for subcuenca in range(1, 41):    
    
            
    # Filtrar los datos por subcuenca
    subcuenca_data = data[data['Subcuenca'] == subcuenca]
            
    # Obtener el nombre de la celda de AEMET y ECMWF
    aemet_celda = subcuenca_data['AEMET_Celda'].iloc[0]
    ecmwf_celda = subcuenca_data['ECMWF_Celda'].iloc[0]
            
    # Leer datos de precipitación AEMET
    pcp_AEMET_file = os.path.join(pcp_AEMET_dir, f'{aemet_celda}_PCP.txt')
    pcp_AEMET_data = np.loadtxt(pcp_AEMET_file, skiprows=1)  # Saltar la primera fila    
    # Leer datos de temperatura AEMET
    tmp_AEMET_file = os.path.join(tmp_AEMET_dir, f'{aemet_celda}_TMP.txt')
    tmp_AEMET_data = np.genfromtxt(tmp_AEMET_file, delimiter=',', skip_header=1)  # Saltar la primera fila
    # Separar datos de temperatura en mínima y máxima
    tmp_min_AEMET_data = tmp_AEMET_data[:, 1]  # Segunda columna para temperatura mínima
    tmp_max_AEMET_data = tmp_AEMET_data[:, 0]  # Primera columna para temperatura máxima
    # Definir fechas desde el 1/1/1951 hasta la longitud de los datos
    start_date = '1951-01-01'
    end_date = pd.Timestamp(start_date) + pd.Timedelta(days=len(pcp_AEMET_data)-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D') 
    # Crear DataFrames con fechas como índice
    pcp_AEMET_df = pd.DataFrame(pcp_AEMET_data, index=dates, columns=['Precipitacion'])
    tmp_min_AEMET_df = pd.DataFrame(tmp_min_AEMET_data, index=dates, columns=['Temperatura_Minima'])
    tmp_max_AEMET_df = pd.DataFrame(tmp_max_AEMET_data, index=dates, columns=['Temperatura_Maxima'])
    
    # Agregar datos diarios a valores mensuales
    pcp_AEMET_monthly = pcp_AEMET_df.resample('ME').sum()  # Suma de precipitación mensual
    tmp_min_AEMET_monthly = tmp_min_AEMET_df.resample('ME').mean()  # Media de temperatura mínima mensual
    tmp_max_AEMET_monthly = tmp_max_AEMET_df.resample('ME').mean()  # Media de temperatura máxima mensual


    # Iterar sobre cada mes
    for mes in meses:
        # Inicializar un DataFrame vacío para almacenar el sesgo de cada año
        df_pcp_ECMWF = pd.DataFrame(index=range(7))
        df_pcp_mean_ECMWF = pd.DataFrame(index=range(7))
        df_tmin_ECMWF = pd.DataFrame(index=range(7))
        df_tmin_mean_ECMWF = pd.DataFrame(index=range(7))
        df_tmax_ECMWF = pd.DataFrame(index=range(7))
        df_tmax_mean_ECMWF = pd.DataFrame(index=range(7))
        
        df_pcp_AEMET = pd.DataFrame(index=range(7))
        df_tmin_AEMET = pd.DataFrame(index=range(7))
        df_tmax_AEMET = pd.DataFrame(index=range(7))
        
        df_coef_pcp = pd.DataFrame(index=range(7))
        df_coef_tmax = pd.DataFrame(index=range(7))   
        df_coef_tmin = pd.DataFrame(index=range(7))   
        df_coef_mean_pcp = pd.DataFrame(index=range(7))
        df_coef_mean_tmax = pd.DataFrame(index=range(7))   
        df_coef_mean_tmin = pd.DataFrame(index=range(7))   
        primer_dia = f'{mes}-02-'
 
        for year in years:
            # Crear DataFrames vacíos para ECMWF
            pcp_ECMWF_df = pd.DataFrame()
            tmp_min_ECMWF_df = pd.DataFrame()
            tmp_max_ECMWF_df = pd.DataFrame()
        
            # Leer datos de precipitación ECMWF
            pcp_ECMWF_file = os.path.join(tp_dir, f'{ecmwf_celda}_tp_{mes}_{year}.csv')
            pcp_ECMWF_data = pd.read_csv(pcp_ECMWF_file, header=None)  # No es necesario saltar la primera fila
            # Eliminar filas con todas las celdas NaN
            pcp_ECMWF_data_clean = pcp_ECMWF_data.dropna()       
            
            # Leer datos de temperatura mínima ECMWF
            t2m_min_ECMWF_file = os.path.join(t2m_min_dir, f'{ecmwf_celda}_t2m_min_{mes}_{year}.csv')
            t2m_min_ECMWF_data = pd.read_csv(t2m_min_ECMWF_file,header=None)  # No es necesario saltar la primera fila
            t2m_min_ECMWF_data_clean = t2m_min_ECMWF_data.dropna()
                
            # Leer datos de temperatura máxima ECMWF
            t2m_max_ECMWF_file = os.path.join(t2m_max_dir, f'{ecmwf_celda}_t2m_max_{mes}_{year}.csv')
            t2m_max_ECMWF_data = pd.read_csv(t2m_max_ECMWF_file,header=None)  # No es necesario saltar la primera fila
            t2m_max_ECMWF_data_clean = t2m_max_ECMWF_data.dropna()
            
            # Agregar índice de fecha            
            dates = pd.date_range(start=primer_dia + str(year), periods=len(pcp_ECMWF_data_clean), freq='D')
            pcp_ECMWF_data_clean.index = dates 
            # Agregar índice de fecha            
            dates = pd.date_range(start=primer_dia + str(year), periods=len(t2m_min_ECMWF_data_clean), freq='D')
            t2m_min_ECMWF_data_clean.index = dates 
            t2m_max_ECMWF_data_clean.index = dates 

            # Calcular la agregación mensual para cada columna
            pcp_ECMWF_monthly = pcp_ECMWF_data_clean.resample('ME').sum()
            t2m_min_ECMWF_monthly = t2m_min_ECMWF_data_clean.resample('ME').mean()
            t2m_max_ECMWF_monthly = t2m_max_ECMWF_data_clean.resample('ME').mean()

    
            # Obtener el "mean ensemble forecast"
            # Calcular el promedio de todas las columnas 
            pcp_ECMWF_monthly_mean = pcp_ECMWF_monthly.mean(axis=1)
            t2m_min_ECMWF_monthly_mean = t2m_min_ECMWF_monthly.mean(axis=1)
            t2m_max_ECMWF_monthly_mean = t2m_max_ECMWF_monthly.mean(axis=1)
  
            # Obtener las fechas mensuales de ECMWF
            fechas_ecmwf = pcp_ECMWF_monthly.index
            # Seleccionar solo las filas de AEMET que tienen fechas coincidentes con las de ECMWF
            pcp_AEMET_monthly_seleccionado = pcp_AEMET_monthly.loc[fechas_ecmwf]
            fechas_ecmwf = t2m_max_ECMWF_monthly.index
            tmp_min_AEMET_monthly_seleccionado = tmp_min_AEMET_monthly.loc[fechas_ecmwf]
            tmp_max_AEMET_monthly_seleccionado = tmp_max_AEMET_monthly.loc[fechas_ecmwf]
           
            # Ajustar los índices de pcp_ECMWF_monthly_mean para que coincidan con pcp_AEMET_monthly_seleccionado
            pcp_ECMWF_monthly_mean.index = pcp_AEMET_monthly_seleccionado.index
            t2m_min_ECMWF_monthly_mean.index = tmp_min_AEMET_monthly_seleccionado.index
            t2m_max_ECMWF_monthly_mean.index = tmp_max_AEMET_monthly_seleccionado.index
            
            
            
            # Calcular el coeficiente entre los valores de precipitación pronosticados por ECMWF y los observados por AEMET
            coef_pcp = 1/pcp_ECMWF_monthly.div(pcp_AEMET_monthly_seleccionado['Precipitacion'], axis='index')
            coef_tmin = 1/t2m_min_ECMWF_monthly.div(tmp_min_AEMET_monthly_seleccionado['Temperatura_Minima'], axis='index')
            coef_tmax = 1/t2m_max_ECMWF_monthly.div(tmp_max_AEMET_monthly_seleccionado['Temperatura_Maxima'], axis='index')
            
            coef_mean_pcp = 1/pcp_ECMWF_monthly_mean.div(pcp_AEMET_monthly_seleccionado['Precipitacion'], axis='index')
            coef_mean_tmin = 1/t2m_min_ECMWF_monthly_mean.div(tmp_min_AEMET_monthly_seleccionado['Temperatura_Minima'], axis='index')
            coef_mean_tmax = 1/t2m_max_ECMWF_monthly_mean.div(tmp_max_AEMET_monthly_seleccionado['Temperatura_Maxima'], axis='index')
            
                    
            # Asignar el coeficiente de este año como una nueva columna en el DataFrame de coeficientes
            # Transponemos la matriz coef_pcp.values[:7] para que las columnas se conviertan en filas
            transposed_coef_pcp = coef_pcp.values[:7].T
            # Iteramos sobre cada columna de transposed_coef_pcp y asignamos a una nueva fila en df_coef_pcp
            for i, col in enumerate(transposed_coef_pcp):
                df_coef_pcp[f'coef_{year}_{i+1}'] = col
            
            df_coef_mean_pcp[f'coef_{year}'] = coef_mean_pcp.values[:7]
            
            # Repite el proceso para las otras variables
            
            # Para tmin
            transposed_coef_tmin = coef_tmin.values[:7].T
            for i, col in enumerate(transposed_coef_tmin):
                df_coef_tmin[f'coef_{year}_{i+1}'] = col
            
            df_coef_mean_tmin[f'coef_{year}'] = coef_mean_tmin.values[:7]
            
            # Para tmax
            transposed_coef_tmax = coef_tmax.values[:7].T
            for i, col in enumerate(transposed_coef_tmax):
                df_coef_tmax[f'coef_{year}_{i+1}'] = col
            
            df_coef_mean_tmax[f'coef_{year}'] = coef_mean_tmax.values[:7]
            
            # Para pcp_ECMWF
            transposed_pcp_ECMWF = pcp_ECMWF_monthly.values[:7].T
            for i, col in enumerate(transposed_pcp_ECMWF):
                df_pcp_ECMWF[f'pcp_ECMWF_{year}_{i+1}'] = col
            
            df_pcp_mean_ECMWF[f'pcp_{year}'] = pcp_ECMWF_monthly_mean.values[:7]
            
            # Para tmin_ECMWF
            transposed_tmin_ECMWF = t2m_min_ECMWF_monthly.values[:7].T
            for i, col in enumerate(transposed_tmin_ECMWF):
                df_tmin_ECMWF[f'tmin_ECMWF_{year}_{i+1}'] = col
            
            df_tmin_mean_ECMWF[f'tmin_{year}'] = t2m_min_ECMWF_monthly_mean.values[:7]
            
            # Para tmax_ECMWF
            transposed_tmax_ECMWF = t2m_max_ECMWF_monthly.values[:7].T
            for i, col in enumerate(transposed_tmax_ECMWF):
                df_tmax_ECMWF[f'tmax_ECMWF_{year}_{i+1}'] = col
            
            df_tmax_mean_ECMWF[f'tmax_{year}'] = t2m_max_ECMWF_monthly_mean.values[:7]
            
            # Para pcp_AEMET
            df_pcp_AEMET[f'pcp_{year}'] = pcp_AEMET_monthly_seleccionado.values[:7]
            
            # Para tmin_AEMET
            df_tmin_AEMET[f'tmin_{year}'] = tmp_min_AEMET_monthly_seleccionado.values[:7]
            
            # Para tmax_AEMET
            df_tmax_AEMET[f'tmax_{year}'] = tmp_max_AEMET_monthly_seleccionado.values[:7]

            
    
        # Guardar los DataFrames en archivos CSV
        directory = 'D:/Seasonal_forecast/Bias_correction_LSTM/Coeficientes/'
        
        # Para coeficientes de pcp
        file_name_pcp = f'coef_pcp_monthly_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_coef_pcp.to_csv(directory + file_name_pcp, index=False)        
        # Para coeficientes de tmin
        file_name_tmin = f'coef_tmin_monthly_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_coef_tmin.to_csv(directory + file_name_tmin, index=False)        
        # Para coeficientes de tmax
        file_name_tmax = f'coef_tmax_monthly_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_coef_tmax.to_csv(directory + file_name_tmax, index=False)


        # Guardar los DataFrames en archivos CSV
        directory = 'D:/Seasonal_forecast/Bias_correction_LSTM/Coeficientes_medios/'
        
        # Para coeficientes de pcp
        file_name_pcp = f'coef_mean_pcp_monthly_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_coef_mean_pcp.to_csv(directory + file_name_pcp, index=False)        
        # Para coeficientes de tmin
        file_name_tmin = f'coef_mean_tmin_monthly_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_coef_mean_tmin.to_csv(directory + file_name_tmin, index=False)        
        # Para coeficientes de tmax
        file_name_tmax = f'coef_mean_tmax_monthly_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_coef_mean_tmax.to_csv(directory + file_name_tmax, index=False)
        
        # Guardar los DataFrames en archivos CSV
        directory = 'D:/Seasonal_forecast/Bias_correction_LSTM/Predicciones_medias_mensuales/'
        
        # Para pcp
        file_name_pcp = f'Pcp_monthly_mean_ECMWF_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_pcp_mean_ECMWF.to_csv(directory + file_name_pcp, index=False)        
        # Para tmin
        file_name_tmin = f'Tmin_monthly_mean_ECMWF_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_tmin_mean_ECMWF.to_csv(directory + file_name_tmin, index=False)        
        # Para tmax
        file_name_tmax = f'Tmax_monthly_mean_ECMWF_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_tmax_mean_ECMWF.to_csv(directory + file_name_tmax, index=False) 
        
        # Guardar los DataFrames en archivos CSV
        directory = 'D:/Seasonal_forecast/Bias_correction_LSTM/Predicciones_mensuales/'
        
        # Para pcp
        file_name_pcp = f'Pcp_monthly_ECMWF_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_pcp_ECMWF.to_csv(directory + file_name_pcp, index=False)        
        # Para tmin
        file_name_tmin = f'Tmin_monthly_ECMWF_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_tmin_ECMWF.to_csv(directory + file_name_tmin, index=False)        
        # Para tmax
        file_name_tmax = f'Tmax_monthly_ECMWF_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_tmax_ECMWF.to_csv(directory + file_name_tmax, index=False) 
        
        # Guardar los DataFrames en archivos CSV
        directory = 'D:/Seasonal_forecast/Bias_correction_LSTM/AEMET_mensual/'
        
        # Para pcp
        file_name_pcp = f'Pcp_monthly_AEMET_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_pcp_AEMET.to_csv(directory + file_name_pcp, index=False)        
        # Para tmin
        file_name_tmin = f'Tmin_monthly_AEMET_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_tmin_AEMET.to_csv(directory + file_name_tmin, index=False)        
        # Para tmax
        file_name_tmax = f'Tmax_monthly_AEMET_subcuenca_{subcuenca}_mes_{mes}_AEMET_{aemet_celda}_ECMWF_{ecmwf_celda}.csv'
        df_tmax_AEMET.to_csv(directory + file_name_tmax, index=False) 
        
        
        
