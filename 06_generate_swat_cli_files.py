# -*- coding: utf-8 -*-
"""
Created on Thu May 30 14:12:22 2024

@author: LENOVO
"""

import os
from datetime import datetime

def generar_archivo_cli(ruta, tipo):
    # Obtener todos los nombres de archivo en la carpeta
    nombres_archivos = [f for f in os.listdir(ruta) if f.endswith(f".{tipo}")]
    
    # Verificar si hay exactamente 40 archivos
    if len(nombres_archivos) != 40:
        print(f"Advertencia: La carpeta {ruta} no contiene 40 archivos .{tipo} (contiene {len(nombres_archivos)} archivos).")
        return

    # Crear la cabecera del archivo
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    cabecera = f"{tipo}.cli: {'Precipitation' if tipo == 'pcp' else 'Temperature'} file names - file written by SWAT+ editor {ahora}\n"
    cabecera += "filename\n"
    
    # Crear el contenido del archivo
    contenido = cabecera + "\n".join(nombres_archivos)
    
    # Escribir el contenido en el archivo .cli
    with open(os.path.join(ruta, f"{tipo}.cli"), 'w') as archivo:
        archivo.write(contenido)

def recorrer_carpetas(ruta_base):
    for carpeta_principal in os.listdir(ruta_base):
        ruta_carpeta_principal = os.path.join(ruta_base, carpeta_principal)
        if os.path.isdir(ruta_carpeta_principal):
            for subcarpeta in ['pcp', 'tmp']:
                ruta_subcarpeta = os.path.join(ruta_carpeta_principal, subcarpeta)
                if os.path.isdir(ruta_subcarpeta):
                    generar_archivo_cli(ruta_subcarpeta, subcarpeta)

# Ruta base proporcionada
ruta_base = "D:\\Seasonal_forecast\\Bias_corrected_forecast_monthly\\clima_diario_corregido_para_SWAT"

# Ejecutar la función
recorrer_carpetas(ruta_base)
