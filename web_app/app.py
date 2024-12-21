from flask import Flask, render_template, request, url_for
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/img/uploads'
app.config['PROCESSED_FOLDER'] = 'static/img/processed'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp'}

# Crear directorios si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Función para comprobar si el archivo tiene una extensión válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Ruta principal para cargar la página
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Procesar la imagen
        file = request.files.get('file')  # Obtener el archivo
        if not file or not allowed_file(file.filename):
            return render_template('index.html', error="Por favor, sube una imagen válida.")

        # Guardar la imagen
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Obtener las filas y columnas desde el formulario
        try:
            filas = int(request.form.get('filas', 10))
            columnas = int(request.form.get('columnas', 10))
        except ValueError:
            return render_template('index.html', error="Por favor, ingresa números válidos para filas y columnas.")
        
        # Procesar la imagen y generar las imágenes adicionales
        try:
            mask_image, heatmap_image, superimposed_image = procesar_imagen(file_path, filas, columnas)
        except ValueError as e:
            return render_template('index.html', error=str(e))
        
        # Guardar todas las imágenes procesadas
        mask_path = os.path.join(app.config['PROCESSED_FOLDER'], 'mask.png')
        heatmap_path = os.path.join(app.config['PROCESSED_FOLDER'], 'heatmap.png')
        superimposed_path = os.path.join(app.config['PROCESSED_FOLDER'], 'superimposed.png')

        cv2.imwrite(mask_path, mask_image)
        cv2.imwrite(heatmap_path, heatmap_image)
        cv2.imwrite(superimposed_path, superimposed_image)

        # Enviar las imágenes generadas a la página
        images = {
            "original": url_for('static', filename=f'img/uploads/{filename}'),
            "mask": url_for('static', filename='img/processed/mask.png'),
            "heatmap": url_for('static', filename='img/processed/heatmap.png'),
            "superimposed": url_for('static', filename='img/processed/superimposed.png'),
        }
        return render_template('index.html', images=images)
    
    return render_template('index.html')


def procesar_imagen(image_path, filas, columnas):
    # Cargar la imagen
    imagen = cv2.imread(image_path)
    if imagen is None:
        raise ValueError("No se pudo cargar la imagen. Verifica el archivo y su formato.")

    print(f"Imagen cargada correctamente: {image_path}")

    # Convertir la imagen a HSV
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Definir el rango de color blanco para la máscara
    bajo_blanco = np.array([0, 0, 200], dtype=np.uint8)
    alto_blanco = np.array([180, 50, 255], dtype=np.uint8)

    # Crear una máscara para el color blanco
    mascara_blanco = cv2.inRange(hsv, bajo_blanco, alto_blanco)
    if mascara_blanco is None or mascara_blanco.size == 0:
        raise ValueError("La máscara de blanco no se generó correctamente.")

    # Rango de color verde (para las palmeras de plástico)
    # Ajusta estos valores según el color de las palmeras de plástico en tu imagen
    bajo_verde = np.array([35, 50, 50], dtype=np.uint8)
    alto_verde = np.array([85, 255, 255], dtype=np.uint8)

    # Crear una máscara para las palmeras (usando el rango de verde)
    mascara_palmeras = cv2.inRange(hsv, bajo_verde, alto_verde)
    if mascara_palmeras is None or mascara_palmeras.size == 0:
        raise ValueError("La máscara de palmeras no se generó correctamente.")

    # Dimensiones de la imagen
    altura, ancho = mascara_blanco.shape
    if altura == 0 or ancho == 0:
        raise ValueError("La imagen no tiene dimensiones válidas.")

    # Crear la imagen de la máscara en negro
    mascara_coloreada = np.zeros((altura, ancho, 3), dtype=np.uint8)  # Imagen en negro (todas las celdas en negro)

    # Asignar el color blanco a los pellets blancos en la máscara
    mascara_coloreada[mascara_blanco == 255] = [255, 255, 255]  # Pellets blancos en blanco

    # Asignar el color verde a las palmeras en la máscara
    mascara_coloreada[mascara_palmeras == 255] = [0, 255, 0]  # Palmeras en verde

    # El resto de la máscara ya es negro, ya que la hemos inicializado con ceros

    # Crear el mapa de calor con las intensidades
    heatmap = np.zeros((filas, columnas), dtype=float)

    # Calcular tamaño de cada celda
    alto_celda = altura // filas
    ancho_celda = ancho // columnas

    # Calcular la intensidad total de los píxeles en cada celda
    for i in range(filas):
        for j in range(columnas):
            y1, y2 = i * alto_celda, (i + 1) * alto_celda
            x1, x2 = j * ancho_celda, (j + 1) * ancho_celda
            celda_blanco = mascara_blanco[y1:y2, x1:x2]
            celda_palmera = mascara_palmeras[y1:y2, x1:x2]

            # Calcular la intensidad de la celda (número de píxeles blancos)
            intensidad_blanco = np.sum(celda_blanco == 255)
            intensidad_palmera = np.sum(celda_palmera == 255)

            # Si la celda tiene palmeras, asignamos un valor negativo
            if intensidad_palmera > 0:
                heatmap[i, j] = -1  # Asignamos un valor negativo a las palmeras
            else:
                heatmap[i, j] = intensidad_blanco  # Para las otras celdas, dejamos el valor normal

    # Normalizar el mapa de calor para que los valores estén en el rango [0, 1]
    max_intensidad = np.max(heatmap)  # Obtenemos la máxima intensidad
    min_intensidad = np.min(heatmap)  # Obtenemos la mínima intensidad

    # Si la intensidad máxima es mayor que 0, normalizamos los valores
    if max_intensidad > 0:
        heatmap_normalizado = (heatmap - min_intensidad) / (max_intensidad - min_intensidad)
    else:
        heatmap_normalizado = heatmap  # Si todos los valores son 0, no normalizamos

    # Escalar el valor normalizado de [0, 1] a [0, 10]
    heatmap_normalizado_10 = heatmap_normalizado * 10

    np.set_printoptions(suppress=True, precision=2)  # 'suppress' evita la notación científica, 'precision' controla decimales

    # Imprimir la matriz normalizada de intensidades entre 0 y 10
    print("Matriz normalizada del mapa de calor (de 0 a 10):")
    print(heatmap_normalizado_10)

    # Crear una imagen vacía para el mapa de calor
    heatmap_image = np.zeros((altura, ancho), dtype=np.uint8)

    # Rellenar cada celda con su intensidad correspondiente
    for i in range(filas):
        for j in range(columnas):
            y1, y2 = i * alto_celda, (i + 1) * alto_celda
            x1, x2 = j * ancho_celda, (j + 1) * ancho_celda
            # Convertir la intensidad normalizada de [0, 10] a un valor en el rango [0, 255]
            intensidad = int(heatmap_normalizado_10[i, j] * 25.5)  # Multiplicamos por 25.5 para escalar de [0, 10] a [0, 255]
            # Si la celda tiene un valor negativo (palmeras), lo representamos con un valor diferente (por ejemplo, 50)
            if heatmap[i, j] < 0:
                intensidad = 50  # Un valor intermedio para las palmeras (puedes ajustarlo)
            heatmap_image[y1:y2, x1:x2] = intensidad

    # Aplicar el mapa de calor como un colormap
    heatmap_color = cv2.applyColorMap(heatmap_image, cv2.COLORMAP_JET)

    # Superponer el mapa de calor con la imagen original con transparencia
    alpha = 0.6  # Nivel de transparencia
    imagen_superpuesta = cv2.addWeighted(heatmap_color, alpha, imagen, 1 - alpha, 0)

    return mascara_coloreada, heatmap_color, imagen_superpuesta








# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
