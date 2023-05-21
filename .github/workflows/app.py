import os
import pandas as pd
import matplotlib.pyplot as plt
import concurrent.futures
import numpy as np
import re
import seaborn as sns
pd.set_option('display.max_columns', None)
import plotly.graph_objects as go
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Variables de configuración
Tk().withdraw()  # Ocultar la ventana principal de Tkinter
data_folder = askdirectory(title='Selecciona la carpeta de datos')  # Ruta de la carpeta principal donde se encuentran los archivos de datos
output_folder = data_folder  # Ruta de la carpeta donde se guardarán los resultados

especificacion_maxima = float(input('Agregue el límite de especificación Máxima en KN: '))  # Agregar especificación máxima
especificacion_minima = float(input('Agregue el límite de especificación Mínima en KN: '))  # Agregar especificación mínima

contador_seleccionados = 0
archivos_seleccionados = []

def contiene_numero_parte(cadena, numero_parte):
    return numero_parte in cadena

def read_file(path_file: str):
    try:
        with open(path_file, 'r', encoding='latin-1') as f:
            lines = f.readlines()
    except pd.errors.ParserError:
        return {
            "date": [None],
            "hour": [None],
            "sub_assy": [None],
            "total_average": [None],
            "peak_pos": [None],
            "lsl": [None],
            "usl": [None],
            "225mm": [None],
            "250mm": [None],
            "275mm": [None],
            "within_average": [None],
            "pass": [None],
            'path': [path_file]
        }

    df = pd.DataFrame(lines)
    df = df[0].str.split(',', expand=True)
    df.drop([2, 3, 4], axis=1, inplace=True)
    df[0] = df[0].str.replace('"', "")
    df[1] = df[1].str.replace('"', "")

    meta_delimiter = df.index[df[0] == 'Position'][0]
    meta = df.iloc[:meta_delimiter].copy()

    data = df.iloc[meta_delimiter + 1:].copy()
    data[0] = pd.to_numeric(data[0], errors='coerce')
    data[1] = pd.to_numeric(data[1], errors='coerce')

    fig = go.Figure(data=go.Scatter(x=data[0], y=data[1], name='Muestra'))
    fig.add_trace(go.Scatter(x=data[0], y=np.where((data[0] >= 200) & (data[0] <= 300), np.repeat(especificacion_maxima, len(data[0])), np.nan), mode='lines', name='Especificación Máxima'))
    fig.add_trace(go.Scatter(x=data[0], y=np.where((data[0] >= 200) & (data[0] <= 300), np.repeat(especificacion_minima, len(data[0])), np.nan), mode='lines', name='Especificación Mínima'))
    fig.update_layout(title=f'Gráfica de {os.path.basename(path_file)}', xaxis_title='Distance', yaxis_title='Load (KN)')
    fig.show()

    name = meta[1][1]
    name = name.split('\\')[-1].split()[1]

#Agregar parametros de búsqueda
PARAFILE_LIMPIO = ""
PARAFILE_BUSQUEDA = input('Ingrese el nombre completo de la celda del PARAFILE AQUI: ').strip()
PARAFILE_LIMPIO
NUMERO_DE_PARTE = input('Ingrese el NP de Interés para el análisis: ')
    
for root, dirs, files in os.walk(data_folder):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, 'r', encoding='latin-1') as f:
            lines = f.readlines()
            for i in range(len(lines) - 3):
                if 'PARAFILE' in lines[i+2].split(',')[0].strip() and PARAFILE_LIMPIO in lines[i+2].split(',')[1].strip():
                    if 'FILENAME' in lines[i+1].split(',')[0].strip() and NUMERO_DE_PARTE in lines[i+1].split(',')[1].strip():
                        archivos_seleccionados.append(file_path)
                        contador_seleccionados += 1
                        break

print(f"Total de archivos seleccionados: {contador_seleccionados}")

for archivo in archivos_seleccionados:
    read_file(archivo)
