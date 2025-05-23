from PIL import Image, ImageEnhance


from ..utils import convertir_a_png, redimensionar

def process_image(src_path, dst_path, cfg):
    img = Image.open(src_path).convert("RGBA")

    # --- 1) Preprocesado “anticopyright” ---
    if cfg.get("convert_to_png"):
        convertir_a_png(src_path, dst_path)
    if cfg.get("resize_generic"):
        img = redimensionar(img, tuple(cfg["generic_max_size"]))

    # --- 2) DPI & resize exacto ---
    if cfg.get("dpi"):
        img.info['dpi'] = (cfg["dpi"], cfg["dpi"])
    if cfg.get("output_size"):
        img = img.resize(tuple(cfg["output_size"]), Image.LANCZOS)

    # --- 4) Guardado final ---
    img.save(dst_path, format="PNG", optimize=True, dpi=cfg.get("dpi"))