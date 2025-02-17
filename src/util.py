import os
import json
import numpy as np
import urllib
import shutil
import string
import random
from datetime import datetime
from imutils import face_utils

from .config import FORMATO_NUEVA_IMAGEN, REPOSITORIO_DE_IMAGENES_PUBLICAS


def eliminar_archivos_temporales(filename):
    try:
        if type(filename) is list:
            print('Eliminar el archivo temporal {}'.format(filename))
            for name in filename:
                os.remove(name)
        if type(filename) is str:
            print('Eliminar el archivo temporal {}'.format(filename))
            os.remove(filename)
    except Exception as error:
        print('Error al eliminar el archivo temporal {}: {}'.format(filename, error))


def obtener_nombre_nueva_imagen(numero_carpeta_imagen, numero_imagen='0'):
    file_name = FORMATO_NUEVA_IMAGEN.format(numero_carpeta_imagen, numero_imagen)
    full_file_name = os.path.join(REPOSITORIO_DE_IMAGENES_PUBLICAS, 
                        str(numero_carpeta_imagen), 
                        file_name)
    return full_file_name, file_name


def siguiente_numero_carpeta_imagen(azure_storage_cliente_mascotas):
    array_numeros_carpeta = list()
    bloblistingresult = azure_storage_cliente_mascotas.listar_archivos()
    
    for i in bloblistingresult:
        # Número de la carpeta
        dir_numero = i.name.split('/')[1]
        #print(dir_numero)
        array_numeros_carpeta.append(int(dir_numero))
    
    # Si no existen carpetas retorna el nombre de la carpeta '1'
    if len(array_numeros_carpeta) == 0:
        return str(1)
    
    #array_numeros_carpeta = [int(dir_numero) for root, dirs, files in os.walk(REPOSITORIO_DE_IMAGENES_PUBLICAS) if len(dirs) > 0 for dir_numero in dirs]
    array_numeros_carpeta = sorted(array_numeros_carpeta, reverse=True)
    print('Siguiente número de carpeta: ', int(array_numeros_carpeta[0] + 1))
    return str(int(array_numeros_carpeta[0] + 1))


def get_detection_and_shape(detector, predictor, img):
    dets = detector(img, upsample_num_times=1)
    if len(dets) > 1:
        print(f"Se necesitaba 1 cara, se encontraron {len(dets)}")
        return False, f"Se necesitaba 1 cara, se encontraron {len(dets)}", None
    d = dets[0]
    shape = predictor(img, d.rect)
    shape = face_utils.shape_to_np(shape)
    return True, d, [tuple(x) for x in shape]


def download_image(img_url, img_path):
    try:
        print('Descargando imagen de {}'.format(img_url))
        tmp_path, _ = urllib.request.urlretrieve(img_url)
        print('Imagen descargada ({})'.format(img_url))
        to = img_path
        shutil.copyfile(tmp_path, to)
        print('Imagen descargada de {} y movida a {}'.format(img_url, img_path))
        return True, to
    except Exception as e:
        print('Hubo un error al descargar la imagen desde URL ({}): {}'.format(datetime.now(), e))
        return False, None


def retornar_valor_campo_en_diccionario(diccionario, campo):
    if campo in diccionario:
        return diccionario[campo]
    return None


def existe_campo_en_diccionario(diccionario, campo):
    if campo in diccionario:
        return True
    return False

def obtener_valor_estado_mascota(estado):
    '''
    Valores de estado:
    - 1: perdido (persona que perdió su perro)
    - 2: encontrado (persona encuentra un perro en la calle)
    - 3: baja logica  (cuando el perro hizo el match)
    - 0: empadronado

    Si el estado es 1, entonces retornar 2.
    Si el estado es 2, entonces retornar 1.
    '''
    estado_aux = estado
    if estado == 1:
        estado_aux = 2
    elif estado == 2:
        estado_aux = 1
    return estado_aux


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    '''
    Genera números y letras aleatorias. La longitud de la cadena retornada es 8
    '''
    return ''.join(random.choice(chars) for _ in range(size))


class NumpyValuesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
