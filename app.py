from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import requests
import os
import random

app = Flask(__name__)

# --- Lógica de la Inteligencia Artificial ---
features = ['tipo_producto_general', 'tipo_antojo', 'base', 'tipo_sabor', 'weather']

try:
    # 1. Intenta cargar desde la carpeta raíz (donde ejecutas el script)
    df = pd.read_csv('sales_data.csv')
    df['product_id'] = df['product_id'].astype('category')
except FileNotFoundError:
    try:
        # 2. Si falla, intenta cargar desde la subcarpeta 'data/'
        df = pd.read_csv('data/sales_data.csv')
        df['product_id'] = df['product_id'].astype('category')
    except FileNotFoundError:
        # Si no se encuentra en ninguno de los dos lugares, genera el error.
        print("\n=======================================================")
        print("ERROR CRÍTICO: El archivo sales_data.csv no se encontró.")
        print("Asegúrate de que esté en la misma carpeta que 'app.py' O en la subcarpeta 'data/'.")
        print("=======================================================\n")
        exit()
except Exception as e:
    print(f"Error al cargar o procesar el CSV: {e}")
    exit()

# Continuar con el entrenamiento
X = pd.get_dummies(df[features])
y = df['product_id']

try:
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    print("Modelo de IA entrenado correctamente.")
except Exception as e:
    print(f"Error al entrenar el modelo: {e}. Revisa tus datos.")
    exit()

# --- Funciones de Utilidad ---
def get_weather_data(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city, 'appid': api_key, 'units': 'metric', 'lang': 'es'}
    try:
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()
        if data.get('cod') == 200:
            weather_desc = data['weather'][0]['main'].lower()
            if 'cloud' in weather_desc or 'mist' in weather_desc or 'fog' in weather_desc:
                return 'nublado'
            elif 'rain' in weather_desc or 'drizzle' in weather_desc or 'thunderstorm' in weather_desc:
                return 'lluvioso'
            elif 'clear' in weather_desc:
                return 'soleado'
            else:
                return 'soleado'
        else:
            # Error de API, usa default
            pass 
    except requests.exceptions.RequestException:
        # Error de conexión, usa default
        pass 
    return 'soleado' # Clima por defecto en caso de fallo

# --- BASE DE DATOS DE PRODUCTOS ACTUALIZADA ---
PRODUCTS_DB = {
    # ...........................................PALETAS...........................#
    'Paleta de Maracuya': {'name': 'Paleta de Maracuya', 'price': '$25', 'image': 'Pmaracuya.png', 'justification': 'Un toque ácido y tropical, ideal para refrescar.', 'category': 'Paletas'},
    'Paleta de Piña': {'name': 'Paleta de Piña', 'price': '$25', 'image': 'Ppiña.png', 'justification': 'Dulce y refrescante, sabor que transporta a la playa.', 'category': 'Paletas'},
    'Paleta de Queso': {'name': 'Paleta de Queso', 'price': '$25', 'image': 'Pqueso.png', 'justification': 'Cremosa y dulce, una combinación inesperada que encanta.', 'category': 'Paletas'},
    'Paleta de Cajeta ': {'name': 'Paleta de Cajeta ', 'price': '$25', 'image': 'Pcajeta.png', 'justification': 'Un clásico mexicano, dulce y cremoso con sabor a leche quemada.', 'category': 'Paletas'},
    'Paleta de Uva ': {'name': 'Paleta de Uva ', 'price': '$25', 'image': 'Puva.png', 'justification': 'Dulce y jugosa, perfecta para el antojo de fruta.', 'category': 'Paletas'},
    'Paleta de Aroz c/Leche ': {'name': 'Paleta de Aroz c/Leche ', 'price': '$25', 'image': 'Parroz.png', 'justification': 'El postre casero convertido en paleta, cremosa y reconfortante.', 'category': 'Paletas'},
    'Paleta de Fresas c/Crema': {'name': 'Paleta de Fresas c/Crema', 'price': '$25', 'image': 'Pfresascrema.png', 'justification': 'La mezcla perfecta de fruta dulce y cremosidad.', 'category': 'Paletas'},
    'Paleta de Chocolate': {'name': 'Paleta de Chocolate', 'price': '$25', 'image': 'Pchocolate.png', 'justification': 'Un clásico irresistible, dulce y profundo sabor a cacao.', 'category': 'Paletas'},
    'Paleta de Tamarindo': {'name': 'Paleta de Tamarindo', 'price': '$25', 'image': 'Ptamarindo.png', 'justification': 'Ácida y un poco dulce, sabor tradicional que despierta.', 'category': 'Paletas'},
    'Paleta de Nuez': {'name': 'Paleta de Nuez', 'price': '$25', 'image': 'Pnuez.png', 'justification': 'Cremosa, dulce y con trocitos de nuez, ideal para un antojo completo.', 'category': 'Paletas'},
    'Paleta de Mango': {'name': 'Paleta de Mango', 'price': '$25', 'image': 'Pmango.png', 'justification': 'El sabor tropical por excelencia, dulce y vibrante.', 'category': 'Paletas'},
    'Paleta de Coco': {'name': 'Paleta de Coco', 'price': '$25', 'image': 'Pcoco.png', 'justification': 'Exótica y cremosa, te hará sentir en el paraíso.', 'category': 'Paletas'},
    'Paleta de Fresa ': {'name': 'Paleta de Fresa ', 'price': '$25', 'image': 'Pfresa.png', 'justification': 'Sabor dulce y clásico, una opción que nunca falla.', 'category': 'Paletas'},
    'Paleta de Limon ': {'name': 'Paleta de Limon ', 'price': '$25', 'image': 'Plimon.png', 'justification': 'Extremadamente refrescante y ácida, el mejor remedio para el calor.', 'category': 'Paletas'},
    'Paleta de Naranja ': {'name': 'Paleta de Naranja ', 'price': '$25', 'image': 'Pnaranja.png', 'justification': 'Cítrica y dulce, como un rayo de sol refrescante.', 'category': 'Paletas'},
    'Paleta de Chicle': {'name': 'Paleta de Chicle', 'price': '$25', 'image': 'Pchicle.png', 'justification': 'Divertida y dulce, perfecta para un gusto original.', 'category': 'Paletas'},

    #...........................................HELADOS...........................#
    'Helado de Frutos': {'name': 'Helado de Frutos', 'price': '$35', 'image': 'HAfrutos.png', 'justification': 'Nieve de sabores de bosque, ligera y ligeramente ácida.', 'category': 'Helados'},
    'Helado de Kiwi': {'name': 'Helado de Kiwi', 'price': '$35', 'image': 'HAkiwi.png', 'justification': 'Nieve exótica y refrescante con un toque ácido.', 'category': 'Helados'},
    'Helado de Limon': {'name': 'Helado de Limon', 'price': '$35', 'image': 'HAlimon.png', 'justification': 'Nieve ácida y potente, el sabor más refrescante.', 'category': 'Helados'},
    'Helado de Mango': {'name': 'Helado de Mango', 'price': '$35', 'image': 'HAmango.png', 'justification': 'Nieve de mango tropical, dulce y con cuerpo.', 'category': 'Helados'},
    'Helado de Piña': {'name': 'Helado de Piña', 'price': '$35', 'image': 'HApiña.png', 'justification': 'Nieve de piña, un sabor tropical y ligeramente ácido.', 'category': 'Helados'},
    'Helado de Beso de angel': {'name': 'Helado de Beso de angel', 'price': '$35', 'image': 'HLbesoangel.png', 'justification': 'Cremoso, dulce y suave, una delicia celestial.', 'category': 'Helados'},
    'Helado de Cafe': {'name': 'Helado de Cafe', 'price': '$35', 'image': 'HLcafe.png', 'justification': 'Un postre cremoso con el toque amargo y estimulante del café.', 'category': 'Helados'},
    'Helado de Chocolate': {'name': 'Helado de Chocolate', 'price': '$35', 'image': 'HLchocolate.png', 'justification': 'El clásico cremoso y rico en cacao, perfecto para los amantes del dulce.', 'category': 'Helados'},
    'Helado de Chocomenta': {'name': 'Helado de Chocomenta', 'price': '$35', 'image': 'HLchocomenta.png', 'justification': 'La frescura de la menta con la cremosidad del chocolate.', 'category': 'Helados'},
    'Helado de Coco': {'name': 'Helado de Coco', 'price': '$35', 'image': 'HLcoco.png', 'justification': 'Cremoso y tropical, con trocitos de coco real.', 'category': 'Helados'},
    'Helado de Fresa': {'name': 'Helado de Fresa', 'price': '$35', 'image': 'HLfresa.png', 'justification': 'Helado cremoso con el sabor dulce y natural de la fresa.', 'category': 'Helados'},
    'Helado de Fresas c/Crema': {'name': 'Helado de Fresas c/Crema', 'price': '$35', 'image': 'HLfresascrema.png', 'justification': 'El postre clásico en helado, dulce y muy cremoso.', 'category': 'Helados'},
    'Helado de Oreo ': {'name': 'Helado de Oreo ', 'price': '$35', 'image': 'HLoreo.png', 'justification': 'Cremoso y lleno de trocitos de galleta, un postre delicioso.', 'category': 'Helados'},
    'Helado de Pay de limon': {'name': 'Helado de Pay de limon', 'price': '$35', 'image': 'HLpaylimon.png', 'justification': 'Dulce y ácido, con sabor a postre casero.', 'category': 'Helados'},
    'Helado de Vainilla': {'name': 'Helado de Vainilla', 'price': '$35', 'image': 'HLvainilla.png', 'justification': 'El helado más versátil y cremoso, un deleite clásico.', 'category': 'Helados'},
    'Helado de Zarzamora c/Queso ': {'name': 'Helado de Zarzamora c/Queso ', 'price': '$35', 'image': 'HLzarzamoraqueso.png', 'justification': 'La acidez de la zarzamora equilibrada con la cremosidad del queso.', 'category': 'Helados'},
    'Helado de Pistache': {'name': 'Helado de Pistache', 'price': '$35', 'image': 'HLpistache.png', 'justification': 'Helado con el sabor delicado y único del pistache.', 'category': 'Helados'},
    'Helado de Ferrero': {'name': 'Helado de Ferrero', 'price': '$35', 'image': 'HLferrero.png', 'justification': 'Una experiencia de sabor a chocolate y avellanas.', 'category': 'Helados'},
    'Bola EXTRA': {'name': 'Bola EXTRA', 'price': '$10', 'image': 'extra.png', 'justification': 'Una bola extra de tu sabor favorito para completar tu antojo.', 'category': 'Helados'},

    #...........................................AGUAS...........................#
    'Agua CH de Frutas ': {'name': 'Agua CH de Frutas ', 'price': '$25', 'image': 'Afrutasm.png', 'justification': 'Agua fresca de frutas naturales en tamaño chico, dulce y revitalizante.', 'category': 'Aguas'},
    'Agua CH de Horchata': {'name': 'Agua CH de Horchata', 'price': '$25', 'image': 'Ahorchatam.png', 'justification': 'Agua chica de horchata, cremosa, dulce y refrescante.', 'category': 'Aguas'},
    'Agua CH de Chia con limon': {'name': 'Agua CH de Chia con limon', 'price': '$25', 'image': 'Achiam.png', 'justification': 'Agua chica de chía con limón, ácida e hidratante.', 'category': 'Aguas'},
    'Agua CH de Coco c/Nuez': {'name': 'Agua CH de Coco c/Nuez', 'price': '$25', 'image': 'Acocom.png', 'justification': 'Agua chica de coco con nuez, dulce y con textura.', 'category': 'Aguas'},
    'Agua CH de Jamaica': {'name': 'Agua CH de Jamaica', 'price': '$25', 'image': 'Ajamaicam.png', 'justification': 'Agua chica de jamaica, ácida y con un toque floral.', 'category': 'Aguas'},
    'Agua CH de Piña colada': {'name': 'Agua CH de Piña colada', 'price': '$25', 'image': 'Apiñam.png', 'justification': 'Agua chica con sabor a piña colada, tropical y cremosa.', 'category': 'Aguas'},
    'Agua CH de Cafe': {'name': 'Agua CH de Cafe', 'price': '$25', 'image': 'Acafem.png', 'justification': 'Agua chica de café, la energía que necesitas para seguir.', 'category': 'Aguas'},
    'Agua CH de Citricos': {'name': 'Agua CH de Citricos', 'price': '$25', 'image': 'Acitricosm.png', 'justification': 'Agua chica de cítricos, una explosión de sabor ácido y refrescante.', 'category': 'Aguas'},
    'Agua G de Frutas ': {'name': 'Agua G de Frutas ', 'price': '$35', 'image': 'Afrutasg.png', 'justification': 'Agua fresca de frutas naturales en tamaño grande, ideal para compartir.', 'category': 'Aguas'},
    'Agua G de Horchata': {'name': 'Agua G de Horchata', 'price': '$35', 'image': 'Ahorchatag.png', 'justification': 'Agua grande de horchata, el clásico cremoso en su mejor versión.', 'category': 'Aguas'},
    'Agua G de Chia con limon': {'name': 'Agua G de Chia con limon', 'price': '$35', 'image': 'Achiag.png', 'justification': 'Agua grande de chía con limón, la opción más saludable y refrescante.', 'category': 'Aguas'},
    'Agua G de Coco c/Nuez': {'name': 'Agua G de Coco c/Nuez', 'price': '$35', 'image': 'Acocog.png', 'justification': 'Agua grande de coco con nuez, perfecta para un antojo grande y tropical.', 'category': 'Aguas'},
    'Agua G de Jamaica': {'name': 'Agua G de Jamaica', 'price': '$35', 'image': 'Ajamaicag.png', 'justification': 'Agua grande de jamaica, ideal para apagar la sed con un sabor potente.', 'category': 'Aguas'},
    'Agua G de Piña colada': {'name': 'Agua G de Piña colada', 'price': '$35', 'image': 'Apiñag.png', 'justification': 'Agua grande con sabor a piña colada, sabor a vacaciones.', 'category': 'Aguas'},
    'Agua G de Cafe': {'name': 'Agua G de Cafe', 'price': '$35', 'image': 'Acafeg.png', 'justification': 'Agua grande de café, para los que necesitan un extra de energía y sabor.', 'category': 'Aguas'},
    'Agua G de Citricos': {'name': 'Agua G de Citricos', 'price': '$35', 'image': 'Acitricosg.png', 'justification': 'Agua grande de cítricos, refrescante y con vitaminas.', 'category': 'Aguas'},

    #....................................ESPECIALIDADES...........................#
    'Fresas c/Crema': {'name': 'Fresas c/Crema', 'price': '$45', 'image': 'fresascrema.png', 'justification': 'El postre favorito, fresas frescas con una crema dulce y suave.', 'category': 'Especialidades'},
    'Frappe de Oreo': {'name': 'Frappe de Oreo', 'price': '$40', 'image': 'frappeoreo.png', 'justification': 'Bebida helada, cremosidad y trozos de galleta Oreo.', 'category': 'Especialidades'},
    'Banana Split': {'name': 'Banana Split', 'price': '$42', 'image': 'bananasplit.png', 'justification': 'Plátano dividido con helado, crema y tus toppings favoritos.', 'category': 'Especialidades'},
    'Copa de helado Choco': {'name': 'Copa de helado Choco', 'price': '$55', 'image': 'chchocolate.png', 'justification': 'Helado de chocolate en copa con jarabe y chispas, un clásico.', 'category': 'Especialidades'},
    'Copa de helado Napolitano': {'name': 'Copa de helado Napolitano', 'price': '$56', 'image': 'chnapolitano.png', 'justification': 'Una copa con los tres sabores clásicos: vainilla, fresa y chocolate.', 'category': 'Especialidades'},
    'Mangonada': {'name': 'Mangonada', 'price': '$35', 'image': 'mangonada.png', 'justification': 'Dulce, ácido y picante. Mango con chamoy y chile, ¡una explosión de sabor!', 'category': 'Especialidades'},
    'Chocobana': {'name': 'Chocobana', 'price': '$24', 'image': 'chocobana.png', 'justification': 'Plátano congelado cubierto con una capa crujiente de chocolate.', 'category': 'Especialidades'},
    'Sandiwch Helado ': {'name': 'Sandiwch Helado ', 'price': '$25', 'image': 'sandi.png', 'justification': 'Helado entre dos galletas, un postre cremoso y fácil de llevar.', 'category': 'Especialidades'},
    'Canasta de Helado': {'name': 'Canasta de Helado', 'price': '$60', 'image': 'canasta.png', 'justification': 'Tu elección de helado servido en una canasta de waffle crujiente.', 'category': 'Especialidades'},
    'Frape de fresa': {'name': 'Frape de fresa', 'price': '$40', 'image': 'frappefresa.png', 'justification': 'Bebida helada y cremosa con el dulce sabor de la fresa.', 'category': 'Especialidades'},
    'Paleta preparada': {'name': 'Paleta preparada', 'price': '$35', 'image': 'ppreparada.png', 'justification': 'Cualquier paleta bañada en chile, chamoy o limón, ¡personaliza tu antojo!', 'category': 'Especialidades'},
    'Malteadas': {'name': 'Malteadas', 'price': '$65', 'image': 'malteadas.png', 'justification': 'Bebida espesa y cremosa, elige tu sabor favorito y disfrútala.', 'category': 'Especialidades'},
}

# --- Rutas de Flask ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        client_data = request.json
        client_responses = {
            'tipo_producto_general': client_data.get('tipo_producto_general'),
            'tipo_antojo': client_data.get('tipo_antojo'),
            'base': client_data.get('base'),
            'tipo_sabor': client_data.get('tipo_sabor')
        }

        if not all(client_responses.values()):
            return jsonify({'error': 'Faltan respuestas necesarias del cuestionario'}), 400

        # Usa la API Key del entorno o la que tenías por defecto
        api_key = os.environ.get('WEATHER_API_KEY', 'cee0d3d67f8dfd9ff7e84d1f849c884e')
        city = 'Mexico City'
        current_weather = get_weather_data(api_key, city)
        
        # 1. Preparar la entrada para la IA
        input_data = pd.DataFrame([client_responses], columns=features)
        input_data['weather'] = current_weather
        
        # 2. Codificar y reindexar (crucial para que coincidan las columnas del entrenamiento)
        input_data_encoded = pd.get_dummies(input_data)
        input_data_encoded = input_data_encoded.reindex(columns=X.columns, fill_value=0)
        
        # 3. Predecir
        try:
             recommended_product_id = model.predict(input_data_encoded)[0]
        except ValueError:
             # Si falla la predicción (columnas nuevas o datos raros), elige un producto al azar
             recommended_product_id = random.choice(list(PRODUCTS_DB.keys()))

        # 4. Chequeo de Coherencia (si el producto no coincide con la categoría elegida)
        chosen_product_type = client_responses['tipo_producto_general']
        predicted_product_category = PRODUCTS_DB.get(recommended_product_id, {}).get('category', '')
        
        # Lógica de corrección: se eliminan las 's' para comparar singular vs plural (Paleta vs Paletas)
        if chosen_product_type.lower().replace('s', '') not in predicted_product_category.lower().replace('s', ''):
            coherent_products = [
                p_id for p_id, p_info in PRODUCTS_DB.items()
                if chosen_product_type.lower().replace('s', '') in p_info['category'].lower().replace('s', '')
            ]
            if coherent_products:
                recommended_product_id = random.choice(coherent_products)

        recommended_product = PRODUCTS_DB.get(recommended_product_id)

        if recommended_product:
            return jsonify({
                'recommended_product': recommended_product,
                'weather': current_weather
            })
        else:
            return jsonify({'error': f'Producto predicho ({recommended_product_id}) no encontrado en la base de datos'}), 404

    except Exception as e:
        # Esto captura cualquier error interno y lo devuelve al cliente para debug
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')