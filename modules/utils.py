import os
from PIL import Image
import shutil
# Extensiones válidas para imágenes
EXTENSIONES_IMAGEN = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff'}

def buscar_imagenes_en_directorio(directorio_base):
    """
    Busca imágenes en el directorio base y sus subdirectorios.

    Args:
        directorio_base (str): ruta del directorio raíz a buscar

    Returns:
        list: lista de rutas de archivos de imagen encontrados
    """
    lista_imagenes = []

    for carpeta_raiz, _, archivos in os.walk(directorio_base):
        for archivo in archivos:
            ruta_completa = os.path.join(carpeta_raiz, archivo)
            _, extension = os.path.splitext(archivo)
            if extension.lower() in EXTENSIONES_IMAGEN:
                lista_imagenes.append(ruta_completa)

    return lista_imagenes

def convertir_a_png(img_path, imagenes_png_dir=None):
    """
    Convierte una imagen a PNG optimizado y opcionalmente la mueve a un directorio común.

    Args:
        img_path (str): Ruta de la imagen a convertir.
        imagenes_png_dir (str|None): Si se indica, ruta del directorio donde colocar
            todas las imágenes en PNG; si no existe, se crea.

    Returns:
        str|None: Ruta del PNG generado o copiado, o None si hubo error.
    """
    if not img_path:
        print("ERROR: No se proporcionó una ruta de imagen válida")
        return None

    if imagenes_png_dir:
        os.makedirs(imagenes_png_dir, exist_ok=True)

    carpeta, nombre = os.path.split(img_path)
    base, ext = os.path.splitext(nombre)
    nombre_png = f"{base}.png"
    destino = os.path.join(imagenes_png_dir or carpeta, nombre_png)

    if ext.lower() == '.png':
        # Imagen ya era PNG: copiarla
        try:
            shutil.copy2(img_path, destino)
            print(f"Copiado → {destino}")
            return destino
        except Exception as e:
            print(f"ERROR copiando {img_path}: {e}")
            return None

    # Para cualquier otro formato, convertir y luego mover/copiar
    try:
        with Image.open(img_path) as img:
            if not img:
                print(f"ERROR abriendo {img_path}")
                return None
            rgba = img.convert('RGBA')
            paletizada = rgba.quantize(method=Image.FASTOCTREE)
            paletizada.save(destino, format='PNG', optimize=True)
            print(f"Convertido → {destino}")
            return destino
    except Exception as e:
        print(f"ERROR procesando {img_path}: {e}")
        return None


def redimensionar_para_cuadro(img_path, max_size, out_path, upscale=False):
    """
    Redimensiona img_path para que quepa dentro de max_size (w, h),
    manteniendo la proporción. Guarda en out_path.
    Args:
        img_path (str): Ruta de la imagen a redimensionar
        max_size (tuple): Tamaño deseado (w, h)
        out_path (str): Ruta donde guardar la imagen redimensionada
        upscale (bool): si es True, también amplía las imágenes
                        menores al máximo para que llenen el cuadro.
    Returns:
        str: Ruta donde se guardó la imagen redimensionada
    """
    if not img_path or not max_size or not out_path:
        raise ValueError("No se permiten valores nulos")

    try:
        with Image.open(img_path) as img:
            # Creamos una copia para no modificar la original en memoria
            img_copy = img.copy()
            # thumbnail ajusta manteniendo proporción y usa LANCZOS por defecto en Pillow>=9
            img_copy.thumbnail(max_size, Image.LANCZOS)
            w0, h0 = img_copy.size
            max_w, max_h = max_size
            ratio = min(max_w / w0, max_h / h0)
            if ratio < 1 or (ratio > 1 and upscale):
                # redimensionar (shrink o upscale) manteniendo proporción
                new_size = (int(w0 * ratio), int(h0 * ratio))
                img_copy = img_copy.resize(new_size, Image.LANCZOS)
                
            # Guardamos con máxima calidad (PNG no usa 'quality')
            img_copy.save(out_path, format='PNG', optimize=True)
    except Exception as e:
        print(f"ERROR al redimensionar {img_path}: {e}")
        return None
    return out_path
