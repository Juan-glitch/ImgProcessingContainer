from typing import List, Tuple
from pathlib import Path
from PIL import Image
import os
import shutil
import yaml
from typing import List, Tuple, Union, Dict, Any

EXTENSIONES_IMAGEN = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
EXTENSIONES_SVG = ['.svg']


def load_config(path: str) -> Dict[str, Any]:
    """
    Carga la configuración desde un archivo YAML.

    Args:
        path (str): ruta del archivo de configuración

    Returns:
        Dict[str, Any]: Diccionario con la configuración cargada.
    """
    # Abrimos el archivo en modo de lectura (con encoding utf-8 porque
    # los archivos de configuración pueden tener caracteres especiales)
    with open(path, encoding="utf-8") as f:
        # Utilizamos la función yaml.safe_load() para cargar el contenido
        # del archivo en un diccionario. Esta función es "segura" porque
        # no permite la ejecución de código arbitrario.
        cfg = yaml.safe_load(f)  # type: ignore

    # Verificamos que la configuración cargada sea un diccionario.
    # Si no lo es, lanzamos una excepción con un mensaje descriptivo.
    if not isinstance(cfg, dict):
        raise ValueError("El archivo de configuración debe ser un diccionario.")
    
    # Finalmente, devolvemos el diccionario cargado
    return cfg
def buscar_imagenes_en_directorio(directorio_base: Path) -> List[Path]:
    """
    Busca imágenes en el directorio base y sus subdirectorios.

    Args:
        directorio_base (Path): ruta del directorio raíz a buscar

    Returns:
        List[Path]: lista de rutas de archivos de imagen encontrados
    """
    lista_imagenes = []

    for carpeta_raiz, _, archivos in os.walk(directorio_base):
        for archivo in archivos:
            ruta_completa = Path(carpeta_raiz) / archivo            
            if ruta_completa.suffix.lower() in EXTENSIONES_IMAGEN:
                lista_imagenes.append(ruta_completa)

    return lista_imagenes


def buscar_svgs_en_directorio(
    directorio_base: Path
) -> List[Path]:
    """
    Busca archivos SVG en el directorio base y subdirectorios.

    Args:
        directorio_base (Path): ruta del directorio raíz a buscar

    Returns:
        List[Path]: lista de rutas de archivos SVG encontrados
    """
    lista_svgs: List[Path] = []

    for carpeta_raiz, _, archivos in os.walk(directorio_base):
        for archivo in archivos:
            ruta_completa = Path(carpeta_raiz) / archivo            
            if ruta_completa.suffix.lower() in EXTENSIONES_SVG:
                lista_svgs.append(ruta_completa)

    return lista_svgs


def convertir_a_png(
    img_path: str,
    output_path: str
) -> Path | None:
    """
    Convierte cualquier imagen a PNG optimizado y la guarda en una ruta de destino.
    Si la imagen de origen es PNG, se copiará; si no, se convertirá a PNG.

    Args:
        img_path (str): Ruta de la imagen de entrada.
        output_path (str): Ruta completa del archivo de salida (incluyendo .png).

    Returns:
        Path|None: Ruta completa del PNG generado o copiado, o None si hubo error.
    """
    # Convertir strings a Path
    img_path = Path(img_path)
    output_path = Path(output_path)

    # Validar archivo de entrada
    if not img_path.is_file():
        print("ERROR: No se proporcionó una ruta de imagen válida")
        return None

    # Forzar extensión .png en destino
    output_path = output_path.with_suffix('.png')

    # Crear directorio de destino si no existe
    destino_dir = output_path.parent
    if destino_dir and not destino_dir.exists():
        os.makedirs(destino_dir, exist_ok=True)

    ext_orig = img_path.suffix.lower()

    # Si ya es PNG, simplemente copiar
    if ext_orig == '.png':
        try:
            shutil.copy2(img_path, output_path)
            print(f"Copiado → {output_path}")
            return output_path
        except Exception as e:
            print(f"ERROR copiando {img_path}: {e}")
            return None

    # Convertir otros formatos a PNG optimizado
    try:
        with Image.open(img_path) as img:
            rgba = img.convert('RGBA')
            paletizada = rgba.quantize(method=Image.FASTOCTREE)
            paletizada.save(output_path, format='PNG', optimize=True)
            print(f"Convertido → {output_path}")
            return output_path
    except Exception as e:
        print(f"ERROR procesando {img_path}: {e}")
        return None


def redimensionar(
    img: Image.Image,
    max_size: Tuple[int, int],
    allow_enlarge: bool = False
) -> Image.Image:
    """
    Redimensiona una imagen para que quepa dentro de max_size (w, h),
    manteniendo la proporción.

    Args:
        img (PIL.Image.Image): Imagen a redimensionar.
        max_size (Tuple[int, int]): Tamaño máximo (w, h).
        allow_enlarge (bool): Si es True, amplía las imágenes
                              menores que max_size. Por defecto False.

    Returns:
        PIL.Image.Image: Imagen redimensionada (PIL). Si no hace falta
                         cambiar tamaño, devuelve una copia.
    """
    w0, h0 = img.size
    max_w, max_h = max_size

    # Proporción para que encaje en (max_w, max_h)
    ratio = min(max_w / w0, max_h / h0)

    # ratio < 1 → reducir; ratio > 1 → ampliar (solo si allow_enlarge)
    if ratio < 1 or (ratio > 1 and allow_enlarge):
        new_size = (round(w0 * ratio), round(h0 * ratio))
        return img.resize(new_size, Image.LANCZOS)
    else:
        # No hace falta redimensionar: devolvemos copia para no mutar original
        return img.copy()

