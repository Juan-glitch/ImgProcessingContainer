import os, yaml
from PIL import Image

from modules.utils import buscar_imagenes_en_directorio
from modules.images.imgPipeline  import process_image
from modules.icons.iconPipeline  import process_icon

# Carga de configuración
with open("config.yml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
IMG_CFG  = cfg["images"]
ICO_CFG  = cfg["icons"]

SRC_ROOT = "./00_Imgs"
DST_ROOT = "./output"

def main():
    archivos = buscar_imagenes_en_directorio(SRC_ROOT)
    for src in archivos:
        rel = os.path.relpath(src, SRC_ROOT)
        dst  = os.path.join(DST_ROOT, rel)
        ext  = os.path.splitext(src)[1].lower()

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        if ext in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
            process_image(src, dst, IMG_CFG)

        elif ext == ".svg":
            process_icon(src, dst, ICO_CFG)

        else:
            continue

        print(f"→ Procesado: {dst}")

if __name__ == "__main__":
    main()
