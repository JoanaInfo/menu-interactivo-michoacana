import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("Iniciando entrenamiento local...")

# 1. Carga de datos
try:
    # Usamos os.path.join para construir la ruta al archivo CSV
    DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'sales_data.csv')
    df = pd.read_csv(DATA_FILE_PATH)
except FileNotFoundError:
    print("ERROR: sales_data.csv no encontrado. Verifica la carpeta 'data/'.")
    exit()

# 2. Preprocesamiento y definición de la IA
features = ['tipo_producto_general', 'tipo_antojo', 'base', 'tipo_sabor', 'weather']
X = pd.get_dummies(df[features])
y = df['product_id']

# 3. Entrenar el modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 4. Guardar el modelo entrenado
# La variable X.columns debe estar disponible para la predicción en el servidor
# La guardamos en un archivo simple
joblib.dump(model, 'modelo_ia.pkl')
joblib.dump(X.columns.tolist(), 'model_columns.pkl') # Guardamos las columnas para usar en la predicción

print("\n-------------------------------------")
print("✅ MODELO GUARDADO EXITOSAMENTE.")
print("Ahora, el archivo 'modelo_ia.pkl' está listo para subir a GitHub.")
print("-------------------------------------")