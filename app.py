from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import requests
import os
import random

app = Flask(__name__)

# --- Lógica de la Inteligencia Artificial ---
try:
    df = pd.read_csv('data/sales_data.csv')
    df['product_id'] = df['product_id'].astype('category')
except FileNotFoundError:
    print("El archivo sales_data.csv no se encontró. Asegúrate de que esté en la carpeta 'data/'.")
    exit()

features = ['tipo_producto_general', 'tipo_antojo', 'base', 'tipo_sabor', 'weather']
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
    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    try:
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()
        if data.get('cod') == 200:
            weather_desc = data['weather'][0]['main'].lower()
            if 'cloud' in weather_desc:
                return 'nublado'
            elif 'rain' in weather_desc:
                return 'lluvioso'
            elif 'clear' in weather_desc:
                return 'soleado'
            else:
                return 'soleado'
        else:
            print(f"Error en la API del clima: {data.get('message', 'Mensaje de error desconocido')}")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión a la API del clima: {e}")
    return 'soleado'

PRODUCTS_DB = {
    'Paleta de Mango': {'name': 'Paleta de Mango', 'price': '$25', 'image': 'mango_pop.png', 'justification': 'Un sabor tropical y dulce que no te puedes perder.', 'category': 'Paleta de Agua'},
    'Paleta de Limon': {'name': 'Paleta de Limón', 'price': '$20', 'image': 'limon_pop.png', 'justification': 'Refrescante y ácida, la mejor opción para un día caluroso.', 'category': 'Paleta de Agua'},
    'Helado de Vainilla': {'name': 'Helado de Vainilla', 'price': '$35', 'image': 'vanilla_ice.png', 'justification': 'Un clásico cremoso y dulce que siempre satisface.', 'category': 'Helado'},
    'Nachos con Queso': {'name': 'Nachos con Queso', 'price': '$50', 'image': 'nachos_cheese.png', 'justification': 'Un snack salado con queso derretido, ideal para compartir.', 'category': 'Especialidad'},
    'Papas Preparadas': {'name': 'Papas Preparadas', 'price': '$40', 'image': 'papas_preparadas.png', 'justification': 'Un platillo salado y picante, perfecto para un antojo.', 'category': 'Especialidad'},
    'Fresas con Crema': {'name': 'Fresas con Crema', 'price': '$60', 'image': 'fresas_con_crema.png', 'justification': 'Un postre dulce y cremoso con el toque de fruta natural.', 'category': 'Especialidad'},
    'Agua de Jamaica': {'name': 'Agua de Jamaica', 'price': '$20', 'image': 'jamaica_water.png', 'justification': 'Una bebida dulce y tropical que hidrata y reconforta.', 'category': 'Agua'},
    'Agua de Tamarindo': {'name': 'Agua de Tamarindo', 'price': '$20', 'image': 'tamarindo_water.png', 'justification': 'Un sabor ácido y tradicional, perfecto para un día soleado.', 'category': 'Agua'},
    'Chamoyada de Mango': {'name': 'Chamoyada de Mango', 'price': '$40', 'image': 'chamoyada_mango.png', 'justification': 'Ácida, picante y dulce, una explosión de sabor que te encantará.', 'category': 'Especialidad'},
    'Helado de Chocolate': {'name': 'Helado de Chocolate', 'price': '$35', 'image': 'chocolate_ice.png', 'justification': 'Un clásico cremoso y dulce que nunca falla.', 'category': 'Helado'},
    'Paleta de Fresa': {'name': 'Paleta de Fresa', 'price': '$25', 'image': 'fresa_pop.png', 'justification': 'Un sabor dulce y tradicional que no te puedes perder.', 'category': 'Paleta de Agua'},
    'Helado de Coco': {'name': 'Helado de Coco', 'price': '$35', 'image': 'coconut_ice.png', 'justification': 'Un clásico tropical y cremoso.', 'category': 'Helado'},
    'Nachos con Chili': {'name': 'Nachos con Chili', 'price': '$55', 'image': 'nachos_chili.png', 'justification': 'Un snack salado con un toque picante, perfecto para un antojo.', 'category': 'Especialidad'},
    'Papas con Chamoy': {'name': 'Papas con Chamoy', 'price': '$45', 'image': 'papas_chamoy.png', 'justification': 'Papas crujientes con un toque de sabor salado y picante.', 'category': 'Especialidad'},
    'Agua de Horchata': {'name': 'Agua de Horchata', 'price': '$20', 'image': 'horchata_water.png', 'justification': 'Una bebida dulce y cremosa que te refresca.', 'category': 'Agua'},
    'Malteada de Chocolate': {'name': 'Malteada de Chocolate', 'price': '$40', 'image': 'chocolate_shake.png', 'justification': 'Una bebida cremoso y dulce, perfecta para un día nublado.', 'category': 'Especialidad'},
    'Nieve de Piña': {'name': 'Nieve de Piña', 'price': '$30', 'image': 'pineapple_ice.png', 'justification': 'Un postre de piña tropical, dulce y refrescante.', 'category': 'Helado'},
    'Nachos con Frijoles': {'name': 'Nachos con Frijoles', 'price': '$55', 'image': 'nachos_beans.png', 'justification': 'Un plato salado y sustancioso, ideal para el almuerzo.', 'category': 'Especialidad'},
    'Copa de Helado de Vainilla': {'name': 'Copa de Helado de Vainilla', 'price': '$45', 'image': 'vanilla_cup.png', 'justification': 'El helado clásico en una copa, perfecta con toppings.', 'category': 'Especialidad'},
    'Malteada de Fresa': {'name': 'Malteada de Fresa', 'price': '$40', 'image': 'fresa_shake.png', 'justification': 'Una malteada de fresa cremosa y dulce.', 'category': 'Especialidad'},
    'Agua de Limón': {'name': 'Agua de Limón', 'price': '$20', 'image': 'limon_water.png', 'justification': 'Una bebida cítrica, ácida y muy refrescante.', 'category': 'Agua'},
    'Agua de Piña': {'name': 'Agua de Piña', 'price': '$20', 'image': 'pineapple_water.png', 'justification': 'Dulce y tropical, un sabor que te transporta a la playa.', 'category': 'Agua'},
    'Copa de Helado de Chocolate': {'name': 'Copa de Helado de Chocolate', 'price': '$45', 'image': 'chocolate_cup.png', 'justification': 'Una rica copa de helado de chocolate con toppings.', 'category': 'Especialidad'},
    'Papas con Valentina': {'name': 'Papas con Valentina', 'price': '$45', 'image': 'papas_valentina.png', 'justification': 'Papas saladas con un toque picante de salsa Valentina.', 'category': 'Especialidad'},
    'Torta Cubana': {'name': 'Torta Cubana', 'price': '$60', 'image': 'torta.png', 'justification': 'Una torta salada y sustanciosa, ideal para el almuerzo.', 'category': 'Especialidad'},
    'Agua de Mango': {'name': 'Agua de Mango', 'price': '$20', 'image': 'mango_water.png', 'justification': 'Una bebida dulce y tropical para un día soleado.', 'category': 'Agua'},
    'Helado de Fresa': {'name': 'Helado de Fresa', 'price': '$35', 'image': 'strawberry_ice.png', 'justification': 'Un helado cremoso y dulce de sabor tradicional.', 'category': 'Helado'},
    'Paleta de Mora': {'name': 'Paleta de Mora', 'price': '$20', 'image': 'mora_pop.png', 'justification': 'Una paleta ácida, perfecta para un antojo.', 'category': 'Paleta de Agua'},
    'Chocobana': {'name': 'Chocobana', 'price': '$25', 'image': 'chocobana.png', 'justification': 'Un postre cremoso de plátano con chocolate.', 'category': 'Especialidad'},
    'Malteada de Vainilla': {'name': 'Malteada de Vainilla', 'price': '$40', 'image': 'vanilla_shake.png', 'justification': 'Una bebida cremosa y dulce con el clásico sabor a vainilla.', 'category': 'Especialidad'},
    'Nachos Mixtos': {'name': 'Nachos Mixtos', 'price': '$60', 'image': 'nachos_mixtos.png', 'justification': 'Nachos salados con una variedad de salsas y aderezos.', 'category': 'Especialidad'},
    'Paleta de Piña Colada': {'name': 'Paleta de Piña Colada', 'price': '$25', 'image': 'pina_colada_pop.png', 'justification': 'Una paleta tropical con sabor a piña colada, sin alcohol.', 'category': 'Paleta de Agua'},
    'Copa de Helado de Coco': {'name': 'Copa de Helado de Coco', 'price': '$45', 'image': 'coconut_cup.png', 'justification': 'Una copa cremosa de helado de coco con toppings.', 'category': 'Especialidad'},
    'Esquites': {'name': 'Esquites', 'price': '$40', 'image': 'esquites.png', 'justification': 'Un platillo picante con un sabor delicioso.', 'category': 'Especialidad'},
    'Fresas con Crema': {'name': 'Fresas con Crema', 'price': '$60', 'image': 'fresas_con_crema.png', 'justification': 'Fresas dulces con crema y un toque de chocolate.', 'category': 'Especialidad'},
    'Frappe de Oreo': {'name': 'Frappe de Oreo', 'price': '$45', 'image': 'oreo_frappe.png', 'justification': 'Un frappe cremoso con trozos de galleta Oreo.', 'category': 'Especialidad'},
    'Agua de Sandia': {'name': 'Agua de Sandia', 'price': '$20', 'image': 'sandia_water.png', 'justification': 'Una bebida dulce y refrescante para un día soleado.', 'category': 'Agua'},
    'Tostilocos': {'name': 'Tostilocos', 'price': '$50', 'image': 'tostilocos.png', 'justification': 'Un snack salado y picante, ideal para compartir.', 'category': 'Especialidad'},
    'Coctel de Frutas con Chile': {'name': 'Coctel de Frutas con Chile', 'price': '$35', 'image': 'frutas_chile.png', 'justification': 'Un coctel de frutas dulces con un toque picante.', 'category': 'Especialidad'},
    'Nieve de Mango': {'name': 'Nieve de Mango', 'price': '$30', 'image': 'mango_ice.png', 'justification': 'Una nieve dulce y tropical, perfecta para un día lluvioso.', 'category': 'Helado'},
    'Agua de Fresa': {'name': 'Agua de Fresa', 'price': '$20', 'image': 'fresa_water.png', 'justification': 'Una bebida dulce y refrescante de sabor tradicional.', 'category': 'Agua'},
    'Paleta de Nuez': {'name': 'Paleta de Nuez', 'price': '$25', 'image': 'nuez_pop.png', 'justification': 'Una paleta cremosa y dulce con trozos de nuez.', 'category': 'Paleta de Leche'},
    'Papas con Salsas': {'name': 'Papas con Salsas', 'price': '$45', 'image': 'papas_salsas.png', 'justification': 'Papas crujientes con una variedad de salsas saladas y picantes.', 'category': 'Especialidad'},
    'Nachos Jalapeños': {'name': 'Nachos Jalapeños', 'price': '$55', 'image': 'nachos_jalapenos.png', 'justification': 'Nachos salados y picantes, perfectos para un antojo fuerte.', 'category': 'Especialidad'},
    'Duraznos con Crema': {'name': 'Duraznos con Crema', 'price': '$60', 'image': 'duraznos_con_crema.png', 'justification': 'Un postre dulce y cremoso para refrescarte.', 'category': 'Especialidad'},
    'Rompope': {'name': 'Rompope', 'price': '$30', 'image': 'rompope.png', 'justification': 'Una bebida cremosa y dulce, ideal para el clima frío.', 'category': 'Especialidad'},
    'Paleta de Tamarindo': {'name': 'Paleta de Tamarindo', 'price': '$20', 'image': 'tamarindo_pop.png', 'justification': 'Una paleta ácida de sabor tradicional.', 'category': 'Paleta de Agua'},
    'Agua de Melon': {'name': 'Agua de Melon', 'price': '$20', 'image': 'melon_water.png', 'justification': 'Una bebida dulce y refrescante, ideal para el calor.', 'category': 'Agua'},
    'Helado de Oreo': {'name': 'Helado de Oreo', 'price': '$35', 'image': 'oreo_ice.png', 'justification': 'Un helado cremoso con trozos de galleta Oreo.', 'category': 'Helado'},
    'Nachos con Carne': {'name': 'Nachos con Carne', 'price': '$60', 'image': 'nachos_carne.png', 'justification': 'Un platillo salado y sustancioso con carne.', 'category': 'Especialidad'},
    'Agua de Frambuesa': {'name': 'Agua de Frambuesa', 'price': '$20', 'image': 'frambuesa_water.png', 'justification': 'Una bebida dulce y refrescante.', 'category': 'Agua'},
    'Paleta de Queso': {'name': 'Paleta de Queso', 'price': '$25', 'image': 'queso_pop.png', 'justification': 'Una paleta cremosa y dulce, perfecta para un antojo diferente.', 'category': 'Paleta de Leche'},
    'Paleta de Mango con Chile': {'name': 'Paleta de Mango con Chile', 'price': '$25', 'image': 'mango_chile_pop.png', 'justification': 'Una paleta dulce y picante, ideal para un día de sol.', 'category': 'Paleta de Agua'},
    'Agua de Maracuyá': {'name': 'Agua de Maracuyá', 'price': '$20', 'image': 'maracuya_water.png', 'justification': 'Una bebida ácida y refrescante, perfecta para el clima nublado.', 'category': 'Agua'},
    'Malteada de Vainilla y Fresa': {'name': 'Malteada de Vainilla y Fresa', 'price': '$45', 'image': 'vanilla_fresa_shake.png', 'justification': 'Una bebida dulce y cremosa con dos sabores clásicos.', 'category': 'Especialidad'},
    'Esquites con Hueso': {'name': 'Esquites con Hueso', 'price': '$45', 'image': 'esquites_hueso.png', 'justification': 'Esquites picantes con un toque de carne, perfectos para un antojo.', 'category': 'Especialidad'},
    'Nachos con Guacamole': {'name': 'Nachos con Guacamole', 'price': '$60', 'image': 'nachos_guacamole.png', 'justification': 'Nachos salados con guacamole cremoso.', 'category': 'Especialidad'},
    'Fresas con Crema y Chocolate': {'name': 'Fresas con Crema y Chocolate', 'price': '$65', 'image': 'fresas_con_crema_chocolate.png', 'justification': 'Fresas dulces con crema y un toque de chocolate.', 'category': 'Especialidad'},
    'Coctel de Toronja': {'name': 'Coctel de Toronja', 'price': '$40', 'image': 'toronja_coctel.png', 'justification': 'Un coctel cítrico y refrescante.', 'category': 'Especialidad'},
    'Helado de Cafe': {'name': 'Helado de Cafe', 'price': '$35', 'image': 'cafe_ice.png', 'justification': 'Un helado cremoso con un sabor a café.', 'category': 'Helado'},
    'Agua de Tamarindo con Chile': {'name': 'Agua de Tamarindo con Chile', 'price': '$20', 'image': 'tamarindo_chile_water.png', 'justification': 'Una bebida ácida y picante que te sorprenderá.', 'category': 'Agua'},
    'Papas Fritas con Limon': {'name': 'Papas Fritas con Limon', 'price': '$35', 'image': 'papas_limon.png', 'justification': 'Papas saladas y crujientes con un toque de limón.', 'category': 'Especialidad'},
    'Paleta de Coco con Leche': {'name': 'Paleta de Coco con Leche', 'price': '$25', 'image': 'coco_leche_pop.png', 'justification': 'Una paleta dulce y cremosa con sabor a coco.', 'category': 'Paleta de Leche'},
    'Frappe de Galleta': {'name': 'Frappe de Galleta', 'price': '$45', 'image': 'galleta_frappe.png', 'justification': 'Un frappe cremoso con trozos de galleta.', 'category': 'Especialidad'},
    'Paleta de Zarzamora': {'name': 'Paleta de Zarzamora', 'price': '$20', 'image': 'zarzamora_pop.png', 'justification': 'Una paleta ácida de sabor del bosque.', 'category': 'Paleta de Agua'},
    'Chocobana con Nuez': {'name': 'Chocobana con Nuez', 'price': '$25', 'image': 'chocobana_nuez.png', 'justification': 'Un postre dulce y cremoso con un toque de nuez.', 'category': 'Especialidad'},
    'Helado de Menta con Chispas': {'name': 'Helado de Menta con Chispas', 'price': '$35', 'image': 'menta_ice.png', 'justification': 'Un helado cremoso y refrescante con chispas de chocolate.', 'category': 'Helado'},
    'Nachos con Jalapeños': {'name': 'Nachos con Jalapeños', 'price': '$55', 'image': 'nachos_jalapenos.png', 'justification': 'Nachos salados con un toque picante de jalapeños.', 'category': 'Especialidad'},
    'Papas a la Diabla': {'name': 'Papas a la Diabla', 'price': '$45', 'image': 'papas_diabla.png', 'justification': 'Papas saladas con una salsa picosa.', 'category': 'Especialidad'},
    'Agua de Guanabana': {'name': 'Agua de Guanabana', 'price': '$20', 'image': 'guanabana_water.png', 'justification': 'Una bebida dulce y tropical que te refresca.', 'category': 'Agua'},
    'Paleta de Mandarina': {'name': 'Paleta de Mandarina', 'price': '$20', 'image': 'mandarina_pop.png', 'justification': 'Una paleta ácida de sabor cítrico.', 'category': 'Paleta de Agua'},
    'Malteada de Coco': {'name': 'Malteada de Coco', 'price': '$40', 'image': 'coco_shake.png', 'justification': 'Una malteada cremosa y dulce con sabor a coco.', 'category': 'Especialidad'},
    'Atole de Vainilla': {'name': 'Atole de Vainilla', 'price': '$25', 'image': 'vainilla_atole.png', 'justification': 'Una bebida cremosa y caliente con sabor a vainilla.', 'category': 'Especialidad'},
    'Tacos de Guisado': {'name': 'Tacos de Guisado', 'price': '$20', 'image': 'tacos_guisado.png', 'justification': 'Un platillo salado y sustancioso.', 'category': 'Especialidad'},
    'Crepas con Cajeta y Nuez': {'name': 'Crepas con Cajeta y Nuez', 'price': '$50', 'image': 'crepas.png', 'justification': 'Un postre dulce y cremoso con cajeta y nuez.', 'category': 'Especialidad'},
    'Frappe de Vainilla': {'name': 'Frappe de Vainilla', 'price': '$45', 'image': 'vainilla_frappe.png', 'justification': 'Un frappe cremoso y dulce con un sabor clásico.', 'category': 'Especialidad'},
    'Agua de Naranja': {'name': 'Agua de Naranja', 'price': '$20', 'image': 'naranja_water.png', 'justification': 'Una bebida cítrica y dulce que te refresca.', 'category': 'Agua'},
    'Duraznos con Crema y Leche Condensada': {'name': 'Duraznos con Crema y Leche Condensada', 'price': '$65', 'image': 'duraznos_leche.png', 'justification': 'Un postre dulce y cremoso con un toque de leche condensada.', 'category': 'Especialidad'}
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

        api_key = os.environ.get('WEATHER_API_KEY', 'cee0d3d67f8dfd9ff7e84d1f849c884e')
        city = 'Mexico City'
        current_weather = get_weather_data(api_key, city)
        
        input_data = pd.DataFrame([client_responses], columns=features)
        input_data['weather'] = current_weather
        
        input_data_encoded = pd.get_dummies(input_data)
        input_data_encoded = input_data_encoded.reindex(columns=X.columns, fill_value=0)
        
        recommended_product_id = model.predict(input_data_encoded)[0]

        chosen_product_type = client_responses['tipo_producto_general']
        predicted_product_category = PRODUCTS_DB.get(recommended_product_id, {}).get('category', '')
        
        if chosen_product_type.lower() not in predicted_product_category.lower():
            coherent_products = [
                p_id for p_id, p_info in PRODUCTS_DB.items()
                if chosen_product_type.lower() in p_info['category'].lower()
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
            return jsonify({'error': 'Product not found in database'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)