from typing import Tuple, Optional, Dict, Any, List
from PIL import Image, ImageEnhance
from ..utils import convertir_a_png, redimensionar, buscar_imagenes_en_directorio
from .imgTransforms import run_transforms
from .upscale import upscale
import os
import shutil
from tqdm import tqdm


def process_image(
    src_path: str,
    dst_path: str,
    cfg: Optional[Dict[str, Any]] = None
) -> None:
    """
    Processes an image according to the given configuration.

    The configuration is a dictionary that can have the following keys:
    - convert_to_png: If True, converts the image to PNG and does nothing else.
    - upscale: If True, applies FSRCNN_x2 super-resolution to the image.
    - resize_generic: A tuple of two integers indicating the image size after
      resizing without maintaining the aspect ratio.
    - dpi: An integer indicating the desired DPI for the image.
    - output_size: A tuple of two integers indicating the exact size of the
      image after resizing while maintaining the aspect ratio.

    If nothing is specified, the image is processed without changes.

    :param src_path: Path to the source image
    :param dst_path: Path to the destination image
    :param cfg: Processing configuration
    :return: None
    """
    # Open the source image and convert it to RGBA format to ensure it has an alpha channel
    img = Image.open(src_path).convert("RGBA")

    # --- 1) Preprocess image for "anticopyright" ---
    if cfg is not None and cfg.get("convert_to_png"):
        # If the configuration specifies to convert to PNG, do so and save directly
        convertir_a_png(src_path, dst_path)
        return

    if cfg is not None and cfg.get("upscale"):
        # If the configuration specifies to upscale, apply super-resolution to enhance image quality
        img = upscale(img)

    if cfg is not None and cfg.get("resize_generic"):
        # If the configuration specifies a generic resize, resize the image without maintaining aspect ratio
        img = redimensionar(img, tuple(cfg["resize_generic"]))

    # --- 2) Set DPI and resize image ---
    dpi_value: Optional[Tuple[int, int]] = None
    if cfg is not None and cfg.get("dpi"):
        # If a DPI value is specified, set it in the image metadata
        dpi_value = (cfg["dpi"], cfg["dpi"])
        img.info['dpi'] = dpi_value

    # --- 3) Save the processed image ---
    if isinstance(img, Image.Image):
        # If the image is still a PIL Image, save it directly in PNG format
        img.save(dst_path, format="PNG", optimize=True, dpi=dpi_value)
    else:
        # If the image was converted to a numpy array during processing, convert it back to PIL and save
        Image.fromarray(img).save(dst_path, format="PNG", optimize=True, dpi=dpi_value)


def batch_process_images(src_dir: str, dst_dir: str, cfg: Dict[str, Any]) -> None:
    """
    Procesa todas las imágenes de un directorio de origen y las guarda en el de destino,
    mostrando una barra de progreso.

    Args:
        src_dir (str): Directorio de origen donde se encuentran las imágenes.
        dst_dir (str): Directorio de destino donde se guardarán las imágenes procesadas.
        cfg (Dict[str, Any]): Configuración para el procesamiento de imágenes.

    Returns:
        None
    """
    os.makedirs(dst_dir, exist_ok=True)
    images: List[os.PathLike] = buscar_imagenes_en_directorio(src_dir)

    # Barra de progreso con tqdm
    for src_path in tqdm(images, desc="Procesando imágenes", unit="imagen"):
        rel_path: str = os.path.relpath(src_path, src_dir)
        name, _ = os.path.splitext(rel_path)
        dst_path: str = os.path.join(dst_dir, f"{name}.png")

        try:
            process_image(str(src_path), dst_path, cfg)
        except Exception as e:
            print(f"Error al procesar {src_path}: {e}")
