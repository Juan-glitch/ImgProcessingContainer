import os
import argparse

from pathlib import Path
from modules.images.imgPipeline import batch_process_images
from modules.icons.iconPipeline import batch_process_svgs



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Procesa imágenes y/o SVGs en lote según una configuración YAML."
    )

    parser.add_argument(
        "-c", "--config",
        type=str,
        required=True,
        help="Ruta al fichero de configuración YAML"
    )

    args = parser.parse_args()

    # Carga de configuración
    cfg = load_config(args.config)

    # Obtiene src y dst del YAML (o usa valores por defecto)
    src_root = Path(cfg.get("src", "./00_Imgs"))
    dst_root = Path(cfg.get("dst", "./output"))
    os.makedirs(dst_root, exist_ok=True)

    # Secciones opcionales
    img_cfg: Dict[str, Any] = cfg.get("images", {})
    ico_cfg: Dict[str, Any] = cfg.get("icons", {})

    # Procesamiento condicional
    if img_cfg:
        print(f"→ Procesando imágenes ráster de '{src_root}' a '{dst_root}'")
        batch_process_images(str(src_root), str(dst_root), img_cfg)
    else:
        print("→ Sección 'images' no encontrada en la configuración. Se omite procesamiento ráster.")

    if ico_cfg:
        print(f"→ Procesando iconos SVG de '{src_root}' a '{dst_root}'")
        batch_process_svgs(str(src_root), str(dst_root), ico_cfg)
    else:
        print("→ Sección 'icons' no encontrada en la configuración. Se omite procesamiento SVG.")

if __name__ == "__main__":
    main()

    print("Proceso finalizado.")