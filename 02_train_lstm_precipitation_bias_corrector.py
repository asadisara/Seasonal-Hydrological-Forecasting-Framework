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

# Definición de los parámetros iniciales
for subcuenca in range(1, 41):
    print(subcuenca)
    mes = 1
    print(mes)
    print('pcp')
    
    # Directorios y patrones de archivo para los datos de entrada
    data_folder_Y = "D:/Seasonal_forecast/Bias_correction_LSTM/Coeficientes_medios"
    filename_pattern_Y = f"coef_mean_pcp_monthly_subcuenca_{subcuenca}_mes_{mes}_"
    data_folder_X = "D:/Seasonal_forecast/Bias_correction_LSTM/Predicciones_medias_mensuales"
    filename_pattern_X = f"Pcp_monthly_mean_ECMWF_subcuenca_{subcuenca}_mes_{mes}_"
    
    # Función para encontrar y cargar los datos
    def load_data(folder, pattern):
        matching_file = None
        for filename in os.listdir(folder):
            if filename.startswith(pattern):
                matching_file = filename
                break
        if matching_file:
            filepath = os.path.join(folder, matching_file)
            return pd.read_csv(filepath)
        else:
            print(f"No se encontró ningún archivo que cumpla con el patrón: {pattern}")
            return None
    
    # Cargar los datos
    df_Y = load_data(data_folder_Y, filename_pattern_Y)
    df_X = load_data(data_folder_X, filename_pattern_X)
    
    if df_Y is not None and df_X is not None:
        # Modificar los nombres de los índices y transponer los DataFrames
        df_Y.index = [f"leadtime_{i}" for i in range(1, len(df_Y) + 1)]
        df_Y_transposed = df_Y.transpose()
        df_X.index = [f"leadtime_{i}" for i in range(1, len(df_X) + 1)]
        df_X_transposed = df_X.transpose()
    
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
    
            if R2[0] > 0.5 and all(not np.isnan(r2) for r2 in R2):
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
    
            filename = f'D:\\Seasonal_forecast\\Bias_correction_LSTM\\Resultados\\LSTM_correction_pcp_monthly_subcuenca_{subcuenca}_mes_{mes}.jpeg'
            plot_model(best_model, to_file=filename, show_shapes=True, show_layer_names=False, dpi=96)
    
            filename = f'D:\\Seasonal_forecast\\Bias_correction_LSTM\\Resultados\\performance_correction_pcp_monthly_subcuenca_{subcuenca}_mes_{mes}.csv'
            results_df.to_csv(filename, index=False)
    
            predictions_filename = f'D:\\Seasonal_forecast\\Bias_correction_LSTM\\Resultados\\coef_correction_pcp_monthly_subcuenca_{subcuenca}_mes_{mes}.csv'
            best_predictions.to_csv(predictions_filename, index=True)
        else:
            print("No se encontró una estructura adecuada de LSTM que cumpla con los criterios.")
