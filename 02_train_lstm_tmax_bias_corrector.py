

# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:21:57 2024

@author: LENOVO
"""

import os
import pandas as pd
import random
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error
from tensorflow.keras.utils import plot_model

# Define los parámetros para el primer modelo
for subcuenca in range(1, 41):
    print(subcuenca)
    mes = 1
    print(mes)
    print('tmax')
    
    ############################ OUTPUT
    
    # Directorio donde se encuentra el archivo CSV
    data_folder = "D:/Seasonal_forecast/Bias_correction_LSTM/Coeficientes_medios"
    
    # Construye el nombre del archivo basado en los parámetros
    filename_pattern = f"coef_mean_tmax_monthly_subcuenca_{subcuenca}_mes_{mes}_"
    
    # Encuentra el nombre del archivo que cumple con el patrón
    matching_file = None
    for filename in os.listdir(data_folder):
        if filename.startswith(filename_pattern):
            matching_file = filename
            break
    
    if matching_file:
        # Lee el archivo y guarda el contenido como DataFrame
        filepath = os.path.join(data_folder, matching_file)
        df_Y= pd.read_csv(filepath)  # Asume que el archivo CSV tiene encabezados y está separado por comas
        # Si deseas guardar el DataFrame en un archivo CSV, puedes hacerlo así:
        # combined_df.to_csv("combined_data.csv", index=False)  # Esto guarda el DataFrame sin incluir el índice en el archivo CSV
    else:
        print("No se encontró ningún archivo que cumpla con el patrón especificado.")
    
    # Modificar los nombres de los índices
    df_Y.index = [f"leadtime_{i}" for i in range(1, len(df_Y) + 1)]
    
    # Transponer el DataFrame
    df_Y_transposed = df_Y.transpose()
    
    ############################ INPUT
    
    # Directorio donde se encuentra el archivo CSV
    data_folder = "D:/Seasonal_forecast/Bias_correction_LSTM/Predicciones_medias_mensuales"
    
    # Construye el nombre del archivo basado en los parámetros
    filename_pattern = f"Tmax_monthly_mean_ECMWF_subcuenca_{subcuenca}_mes_{mes}_"
    
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
    df_X_transposed = df_X.transpose()
    
    #####################  LSTM 
    
    # Normalizar los datos
    scaler_x = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_scaled = scaler_x.fit_transform(df_X_transposed.values)
    y_scaled = scaler_y.fit_transform(df_Y_transposed.values)
    
    # Función para construir y compilar el modelo LSTM
    def build_model(neurons1, neurons2, neurons3, output_neurons):
        model = Sequential([
            LSTM(units=neurons1, activation='relu', return_sequences=True, input_shape=(1, X_scaled.shape[1])),
            Dropout(0.1),
            LSTM(units=neurons2, activation='relu', return_sequences=True),
            Dropout(0.1),
            LSTM(units=neurons3, activation='relu'),
            Dense(units=output_neurons, activation='relu')
        ])
        model.compile(optimizer='adam', loss='mse')
        return model
    
    best_model = None
    best_R2 = -np.inf
    best_rmse_scores = []
    best_predictions = None
    
    # Búsqueda aleatoria de la mejor estructura de la LSTM
    for _ in range(100):  # Intentos aleatorios, ajustar según necesidad
        neurons1 = random.randint(2, 64)
        neurons2 = random.randint(2, 64)
        neurons3 = random.randint(2, 64)
        output_neurons = 7
    
        model = build_model(neurons1, neurons2, neurons3, output_neurons)
        
        all_predictions = []
    
        for i in range(len(X_scaled)):
            print(i)
            X_train = np.delete(X_scaled, i, axis=0)
            y_train = np.delete(y_scaled, i, axis=0)
            X_test = X_scaled[i].reshape(1, 1, -1)
            X_train_reshaped = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
            model.fit(X_train_reshaped, y_train, epochs=150, batch_size=7, verbose=0)
            prediction = model.predict(X_test)
            prediction = scaler_y.inverse_transform(prediction)
            all_predictions.append(prediction[0])
    
        df_all_predictions = pd.DataFrame(all_predictions, columns=df_Y_transposed.columns)
        years = list(range(1981, 2020))
        df_all_predictions.index = years
    
        y_true = scaler_y.inverse_transform(y_scaled)
    
        R2 = []
        rmse_scores = []
    
        for i, column in enumerate(df_all_predictions.columns):
            pearson_corr, _ = pearsonr(y_true[:, i], df_all_predictions[column])
            R2.append(pearson_corr ** 2)
            rmse = np.sqrt(mean_squared_error(y_true[:, i], df_all_predictions[column]))
            rmse_scores.append(rmse)
    
        if R2[0] > 0.45 and all(not np.isnan(r2) for r2 in R2):
            best_model = model
            best_R2 = R2
            best_rmse_scores = rmse_scores
            best_predictions = df_all_predictions
            break
    
    if best_model:
        results_df = pd.DataFrame({
            'R2': best_R2,
            'RMSE': best_rmse_scores
        })
    
        for i, column in enumerate(best_predictions.columns):
            print(f"Lead time {i+1}:")
            print(f"  - R^2: {best_R2[i]}")
            print(f"  - RMSE: {best_rmse_scores[i]}\n")
    
        filename = f'D:\\Seasonal_forecast\\Bias_correction_LSTM\\Resultados\\LSTM_correction_tmax_monthly_subcuenca_{subcuenca}_mes_{mes}.jpeg'
        plot_model(best_model, to_file=filename, show_shapes=True, show_layer_names=False, dpi=96)
    
        filename = f'D:\\Seasonal_forecast\\Bias_correction_LSTM\\Resultados\\performance_correction_tmax_monthly_subcuenca_{subcuenca}_mes_{mes}.csv'
        results_df.to_csv(filename, index=False)
    
        predictions_filename = f'D:\\Seasonal_forecast\\Bias_correction_LSTM\\Resultados\\coef_correction_tmax_monthly_subcuenca_{subcuenca}_mes_{mes}.csv'
        best_predictions.to_csv(predictions_filename, index=True)
    else:
        print("No se encontró una estructura adecuada de LSTM que cumpla con los criterios.")
