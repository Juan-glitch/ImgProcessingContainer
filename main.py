import os
import argparse
from typing import Dict, Any
from pathlib import Path
from modules.images.imgPipeline import batch_process_images
from modules.icons.iconPipeline import batch_process_svgs
from modules.utils import load_config
import sys

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Procesa imágenes y/o SVGs en lote según una configuración YAML."
    )

    parser.add_argument(
        "-c", "--config",
        type=str,
        required=True,
        help="Ruta al fichero de configuración YAML."
    )

    sys.argv += ["-c", "config.yml"]  # Cambia a tu ruta real
    args = parser.parse_args()


    # Cargar configuración desde el archivo YAML
    cfg: Dict[str, Any] = load_config(args.config)

    # Obtener rutas de origen y destino (usar valores por defecto si no se especifican)
    src_root: Path = Path(cfg.get("src", "./00_Imgs"))
    dst_root: Path = Path(cfg.get("dst", "./output"))
    dst_root.mkdir(parents=True, exist_ok=True)

    # Obtener configuración específica de imágenes e iconos
    img_cfg: Dict[str, Any] = cfg.get("images", {})
    ico_cfg: Dict[str, Any] = cfg.get("icons", {})

    # Procesar imágenes raster si se proporciona configuración
    if img_cfg:
        print(f"→ Procesando imágenes ráster desde '{src_root}' hacia '{dst_root}'")
        batch_process_images(str(src_root), str(dst_root), img_cfg)
    else:
        print("→ Sección 'images' no encontrada en la configuración. Se omite el procesamiento de imágenes ráster.")

    # Procesar iconos SVG si se proporciona configuración
    if ico_cfg:
        print(f"→ Procesando iconos SVG desde '{src_root}' hacia '{dst_root}'")
        batch_process_svgs(str(src_root), str(dst_root), ico_cfg)
    else:
        print("→ Sección 'icons' no encontrada en la configuración. Se omite el procesamiento de SVGs.")

    print("Proceso finalizado.")


if __name__ == "__main__":
    main()
    # python main.py -c config.yaml