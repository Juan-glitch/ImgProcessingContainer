# -*- coding: utf-8 -*-
import os
from PIL import Image
from modules.utils import buscar_imagenes_en_directorio
from modules.utils import convertir_a_png
from modules.utils import redimensionar_para_cuadro

# --- Ejecución del pipeline ---

def main():
    # defines
    MAX_WIDTH  = 512
    MAX_HEIGHT = 512

    ruta_directorio = "./00_Imgs"  # Reemplaza esto con la ruta real
    salida_png = "./imagenes_en_png"   # Directorio opcional donde volcar todos los PNG
    imagenes = buscar_imagenes_en_directorio(ruta_directorio)
    
    print(f"Se encontraron {len(imagenes)} imágenes:")

    for img in imagenes:
        nombre_base = os.path.splitext(os.path.basename(img))[0]
        final_png   = os.path.join(salida_png, f"{nombre_base}_resized.png")

        # 1) Convertir a PNG optimizado — pasamos el directorio, no un archivo
        ruta_png = convertir_a_png(img, imagenes_png_dir=salida_png)
        if ruta_png:
            size_kb = os.path.getsize(ruta_png) // 1024
            print(f"{ruta_png} → {size_kb} KB")
        else:
            print(f"ERROR procesando {img}, no se generó PNG válido.")

        print(f"[PNG] {os.path.basename(ruta_png)} → {size_kb} KB")

        # 2) Redimensionar al cuadro delimitante
        redimensionado = redimensionar_para_cuadro(
            ruta_png,
            (MAX_WIDTH, MAX_HEIGHT),
            final_png,
            upscale=True    # <- True para ampliar las imágenes pequeñas
        )
        with Image.open(redimensionado) as im:
            w, h = im.size
        print(f"[RED] {os.path.basename(redimensionado)} → {w}×{h} px\n")

        # (Opcional) borrar el PNG intermedio si solo quieres el final
        os.remove(ruta_png)

    print("Pipeline completado. Revisa:", salida_png)

if __name__ == "__main__":
    main()


    