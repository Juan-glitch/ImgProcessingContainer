import os
from PIL import Image
from typing import Optional, Dict, Any, List, Tuple, Union
import io
import cairosvg
from tqdm import tqdm


def _replace_white(
    img: Image.Image,
    src_rgb: Tuple[int, int, int],
    dst_rgb: Tuple[int, int, int]
) -> Image.Image:
    """Reemplaza todos los píxeles de un color origen con otro color destino."""
    if img is None:
        raise ValueError("No se proporcionó una imagen para reemplazar colores")
    try:
        px = img.load()
    except Exception as e:
        raise ValueError(f"No se pudo cargar la imagen: {e}")

    w, h = img.size
    for x in range(w):
        for y in range(h):
            if px[x, y][:3] == src_rgb:
                # Mantener canal alfa si existe
                alpha = px[x, y][3] if len(px[x, y]) == 4 else 255
                px[x, y] = dst_rgb + (alpha,)
    return img


def _open_source_image(
    src_path: str,
    dpi: int
) -> Image.Image:
    """
    Abre un archivo .svg o .png y devuelve una imagen RGBA.

    - SVG: rasteriza con CairoSVG
    - PNG: abre directamente con PIL

    :raises ValueError: si el formato no es soportado o falla la apertura.
    """
    ext = os.path.splitext(src_path)[1].lower()
    if ext == '.svg':
        try:
            png_bytes = cairosvg.svg2png(url=src_path, dpi=dpi)
            return Image.open(io.BytesIO(png_bytes)).convert('RGBA')
        except Exception as e:
            raise ValueError(f"Error al rasterizar SVG {src_path}: {e}")
    elif ext in ['.png']:
        try:
            img = Image.open(src_path).convert('RGBA')
            img.info['dpi'] = (dpi, dpi)
            return img
        except Exception as e:
            raise ValueError(f"Error al abrir PNG {src_path}: {e}")
    else:
        raise ValueError(f"Formato no soportado: {ext}")


def process_icon(
    src_path: str,
    dst_path: str,
    cfg: Dict[str, Any]
) -> None:
    """
    Procesa un icono (.svg o .png) según configuración:

    - Rasteriza SVG si aplica
    - Redimensiona al max_size por categoría
    - Reemplaza color blanco si indicado
    - Guarda siempre como PNG optimizado

    :param src_path: ruta origen (.svg/.png)
    :param dst_path: ruta destino (sin extensión)
    :param cfg: configuración con claves obligatorias:
        - dpi: int
        - max_size: dict con 'group' o 'recipe': (w, h)
        - white_replace: bool opcional
        - white_src: tuple(r,g,b) opcional
        - white_dst: tuple(r,g,b) opcional
    """
    # Validar cfg mínimo
    if 'dpi' not in cfg or 'max_size' not in cfg:
        raise ValueError("La configuración debe incluir 'dpi' y 'max_size'")

    # Cargar imagen origen
    img = _open_source_image(src_path, cfg['dpi'])

    # Determinar categoría y tamaño máximo
    sizes = cfg['max_size']
    if 'group' in sizes and 'recipe' in sizes:
        raise ValueError("Solo puede haber una categoría en max_size: 'group' o 'recipe'.")
    category = 'group' if 'group' in sizes else 'recipe'
    max_w, max_h = sizes[category]

    # Redimensionar
    img.thumbnail((max_w, max_h), Image.LANCZOS)

    # Reemplazar color blanco si requerido
    if cfg.get('white_replace', False):
        if 'white_src' not in cfg or 'white_dst' not in cfg:
            raise ValueError("Para white_replace se necesitan 'white_src' y 'white_dst'.")
        img = _replace_white(img, tuple(cfg['white_src']), tuple(cfg['white_dst']))

    # Guardar como PNG optimizado
    dst_png = os.path.splitext(dst_path)[0] + '.png'
    os.makedirs(os.path.dirname(dst_png), exist_ok=True)
    try:
        img.save(dst_png, 'PNG', optimize=True, dpi=(cfg['dpi'], cfg['dpi']))
    except Exception as e:
        raise ValueError(f"No se pudo guardar {dst_png}: {e}")


def batch_process_icons(
    src_dir: str,
    dst_dir: str,
    cfg: Dict[str, Any]
) -> None:
    """
    Procesa en lote todos los .svg y .png en un directorio recursivamente.
    Mantiene estructura de carpetas.
    """
    os.makedirs(dst_dir, exist_ok=True)
    # Recorrer archivos
    file_list: List[str] = []
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.lower().endswith(('.svg', '.png')):
                file_list.append(os.path.join(root, f))

    for src_path in tqdm(file_list, desc="Procesando iconos", unit="icono"):
        rel = os.path.relpath(src_path, src_dir)
        dst_path = os.path.join(dst_dir, rel)
        try:
            process_icon(src_path, dst_path, cfg)
        except Exception as e:
            print(f"Error en {src_path}: {e}")
