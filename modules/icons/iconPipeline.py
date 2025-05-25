import os
from PIL import Image
from typing import Optional, Dict, Any, List, Tuple, Union
from ..utils import  buscar_svgs_en_directorio
from tqdm import tqdm
from typing import Union
import io
import cairosvg
from PIL import Image

def _replace_white(img: Image.Image, src_rgb: Tuple[int, int, int], dst_rgb: Tuple[int, int, int]) -> Image.Image:
    """Reemplaza todos los píxeles blancos de una imagen con un color especificado.

    Args:
        img: La imagen que se va a modificar.
        src_rgb: El color RGB original (r, g, b) que se va a reemplazar.
        dst_rgb: El color RGB destino (r, g, b) que se va a asignar.

    Returns:
        La imagen modificada.
    """
    if img is None:
        raise ValueError("No se proporcionó una imagen para reemplazar colores")
    
    try:
        px = img.load()
    except Exception as e:
        raise ValueError("No se pudo cargar la imagen: {}".format(e))
    
    w, h = img.size
    for x in range(w):
        for y in range(h):
            if px[x, y][:3] == src_rgb:
                px[x, y] = dst_rgb + (px[x, y][3],)

    return img

def convertir_svg_a_png(src_svg: str, dpi: int = 96) -> Union[Image.Image, None]:
    """
    Rasteriza un SVG a una imagen PIL usando CairoSVG.

    Args:
        src_svg (str): La ruta del archivo SVG a rasterizar.
        dpi (int): La resolución de salida en píxeles por pulgada.

    Returns:
        Union[Image.Image, None]: La imagen rasterizada como objeto PIL.Image, o None si ocurre un error.

    Raises:
        ValueError: Si no se pudo leer o rasterizar el SVG.
    """
    try:
        png_bytes: bytes = cairosvg.svg2png(url=src_svg, dpi=dpi)
    except Exception as e:
        raise ValueError(f"No se pudo leer o rasterizar el SVG: {e}")

    try:
        return Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    except Exception as e:
        raise ValueError(f"No se pudo leer la imagen PNG generada: {e}")


def process_svg_icon(
    src_path: str,
    dst_path: str,
    cfg: Optional[Dict[str, Any]] = None
) -> None:
    """
    Procesa un icono SVG según la configuración proporcionada.

    La configuración es un diccionario que puede tener las siguientes claves:
    - rasterize_to_png: Si es True, rasteriza el icono SVG a PNG y lo procesa.
    - max_size: Un diccionario con claves "group" y "recipe" que especifican el tamaño máximo para cada categoría.

    Si no se proporciona configuración, el icono se procesa sin cambios.

    :param src_path: Ruta del icono SVG de origen
    :param dst_path: Ruta del icono procesado
    :param cfg: Configuración de procesamiento
    :return: None
    """
    if cfg is None:
        raise ValueError("No se proporcionó una configuración para procesar el icono")

    # Abrir el icono SVG y convertirlo a RGBA
    try:
        img = convertir_svg_a_png(src_path, cfg["dpi"])
        img.info['dpi'] = (cfg["dpi"], cfg["dpi"])
    except KeyError as e:
        raise ValueError(f"La configuración debe tener una clave 'dpi': {e}")
    except Exception as e:
        raise ValueError(f"Error al rasterizar {src_path}: {e}")

    # Rasterizar y procesar icono SVG
    png_dst: str = os.path.splitext(dst_path)[0] + ".png"
    # rasterizar primero
    png_dst: str = os.path.splitext(dst_path)[0] + ".png"
    # rasterizar directamente a PIL.Image
    png_dst: str = os.path.splitext(dst_path)[0] + ".png"


    # Verificar si existen ambas categorías en max_size
    if "group" in cfg["max_size"] and "recipe" in cfg["max_size"]:
        raise ValueError("Solo puede haber una categoría en max_size: group o recipe")

    # Detectar categoría y limitar tamaño
    cat: str = "group" if "group" in cfg["max_size"] else "recipe"
    max_w: int
    max_h: int
    max_w, max_h = tuple(cfg["max_size"][cat])
    img.thumbnail((max_w, max_h), Image.LANCZOS)  # Redimensionar imagen

    # White-wash
    if cfg.get("white_replace"):
        try:
            _replace_white(img,  # Reemplazar colores blancos
                tuple(cfg["white_src"]),
                tuple(cfg["white_dst"])
            )
        except KeyError as e:
            raise ValueError(f"La configuración debe tener las claves 'white_src' y 'white_dst': {e}")

    try:
        img.save(png_dst, "PNG", optimize=True,  # Guardar imagen en PNG
                    dpi=(cfg["dpi"], cfg["dpi"]))
    except IOError as e:
        raise ValueError(f"No se pudo guardar el archivo {png_dst}: {e}")

def batch_process_svgs(src_dir: str, dst_dir: str, cfg: Dict[str, Any]) -> None:
    """
    Copia o convierte SVGs de un directorio de origen al de destino,
    mostrando una barra de progreso.

    Args:
        src_dir (str): Directorio de origen donde se encuentran los SVGs.
        dst_dir (str): Directorio de destino donde se guardarán los SVGs procesados.

    Returns:
        None
    """
    os.makedirs(dst_dir, exist_ok=True)
    svgs: List[os.PathLike] = buscar_svgs_en_directorio(src_dir)

    for src_path in tqdm(svgs, desc="Procesando SVGs", unit="svg"):
        rel_path: str = os.path.relpath(src_path, src_dir)
        dst_path: str = os.path.join(dst_dir, rel_path)

        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        try:
            process_svg_icon(str(src_path), str(dst_path), cfg)
        except Exception as e:
            print(f"Error al procesar {src_path}: {e}")