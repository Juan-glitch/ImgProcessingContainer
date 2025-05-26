import os
import argparse
from typing import Dict, Any, Optional
from pathlib import Path
from modules.images.imgPipeline import batch_process_images
from modules.icons.iconPipeline import batch_process_icons
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
    # Añadir argumento para la ruta del fichero de configuración
    sys.argv += ["-c", "config.yml"]  # Cambia a tu ruta real
    args = parser.parse_args()

    # Cargar configuración desde el archivo YAML
    cfg: Optional[Dict[str, Any]] = load_config(args.config)
    if cfg is None:
        print(f"Error al cargar configuración desde '{args.config}'")
        sys.exit(1)

    # Obtener configuración específica de imágenes e iconos
    img_cfg: Optional[Dict[str, Any]] = cfg.get("images")
    ico_cfg: Optional[Dict[str, Any]] = cfg.get("icons")

    # Procesar imágenes raster si se proporciona configuración
    if img_cfg is not None:
        # Obtener rutas de origen y destino (usar valores por defecto si no se especifican)
        img_src_root: Path = Path(img_cfg.get("src", "./imgsProcesar"))
        img_dst_root: Path = Path(img_cfg.get("dst", "./outputImgs"))
        img_dst_root.mkdir(parents=True, exist_ok=True)
        print(f"→ Procesando imágenes ráster desde '{img_src_root}' hacia '{img_dst_root}'")
        batch_process_images(str(img_src_root), str(img_dst_root), img_cfg)
    else:
        print("→ Sección 'images' no encontrada en la configuración. Se omite el procesamiento de imágenes ráster.")

    # Procesar iconos SVG si se proporciona configuración
    if ico_cfg is not None:
        # Obtener rutas de origen y destino (usar valores por defecto si no se especifican)
        ico_src_root: Path = Path(ico_cfg.get("src", "./iconosProcesar"))
        ico_dst_root: Path = Path(ico_cfg.get("dst", "./outputIcons"))
        ico_dst_root.mkdir(parents=True, exist_ok=True)
        print(f"→ Procesando iconos SVG desde '{ico_src_root}' hacia '{ico_dst_root}'")
        batch_process_icons(str(ico_src_root), str(ico_dst_root), ico_cfg)
    else:
        print("→ Sección 'icons' no encontrada en la configuración. Se omite el procesamiento de SVGs.")

    print("Proceso finalizado.")


if __name__ == "__main__":
    main()
