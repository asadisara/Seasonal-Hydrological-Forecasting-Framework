# -*- coding: utf-8 -*-
"""
Created on Wed May 29 10:29:45 2024

@author: LENOVO
"""

import os
import pandas as pd

# Definir las rutas de las carpetas
carpeta_tmax = r"D:\Seasonal_forecast\Bias_corrected_forecast_monthly\tmp_diarias_corregidas_para_SWAT\tmax_diarias_corregidas_para_SWAT"
carpeta_tmin = r"D:\Seasonal_forecast\Bias_corrected_forecast_monthly\tmp_diarias_corregidas_para_SWAT\tmin_diarias_corregidas_para_SWAT"
output_folder = r"D:\Seasonal_forecast\Bias_corrected_forecast_monthly\clima_diario_corregido_para_SWAT"

# Especifica el mes y la subcuenca
for subcuenca in range(1, 41):
    print(subcuenca)
    mes = 12
    
    # Función para procesar un año
    def procesar_anio(anio):
        # Nombre del mes en texto
        nombre_mes = mes
        # Ruta de la carpeta correspondiente al año y al mes
        carpeta_mes_anio = os.path.join(output_folder, f"{nombre_mes}_{anio}")
    
        # Crear la carpeta de salida si no existe
        os.makedirs(carpeta_mes_anio, exist_ok=True)  
        
        # Crear la carpeta "tmp" dentro de la carpeta del mes y año
        carpeta_tmp = os.path.join(carpeta_mes_anio, "tmp")
        os.makedirs(carpeta_tmp, exist_ok=True)
        
        archivo_tmax = os.path.join(carpeta_tmax, f"Corrected_tmp_subcuenca_{subcuenca}_mes_{mes}_year_{anio}.tmp")
        archivo_tmin = os.path.join(carpeta_tmin, f"Corrected_tmin_subcuenca_{subcuenca}_mes_{mes}_year_{anio}.tmp")
        archivo_salida = os.path.join(carpeta_tmp, f"Corrected_tmp_subcuenca_{subcuenca}.tmp")
    
        # Leer los archivos de entrada
        with open(archivo_tmax, 'r') as file:
            lineas_tmax = file.readlines()
            
        with open(archivo_tmin, 'r') as file:
            lineas_tmin = file.readlines()
    
        # Obtener la cabecera y datos de tmax
        cabecera_tmax = lineas_tmax[:3]
        datos_tmax = [linea.strip().split() for linea in lineas_tmax[3:]]
    
        # Obtener los datos de tmin
        datos_tmin = [linea.strip().split() for linea in lineas_tmin[3:]]
    
        # Combinar los datos
        datos_combinados = []
        for tmax, tmin in zip(datos_tmax, datos_tmin):
            datos_combinados.append(f"{tmax[0]:>4}    {tmax[1]:>2}    {float(tmax[2]):>8.5f}    {float(tmin[2]):>8.5f}\n")
    
        # Escribir el archivo de salida
        with open(archivo_salida, 'w') as file:
            file.writelines(cabecera_tmax)
            file.writelines(datos_combinados)
    
    # Procesar los años desde 1981 hasta 2019
    for year in range(1981, 2020):
        procesar_anio(year)
    
    print("Archivos generados con éxito.")
