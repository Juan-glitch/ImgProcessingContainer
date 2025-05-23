import os, shutil
from PIL import Image

def process_icon(src_path, dst_path, cfg):
    # 1) Copia SVG tal cual
    if cfg.get("copy_svg", False):
        shutil.copy2(src_path, dst_path)

    # 2) Rasterizado y procesado si se pide
    if cfg.get("rasterize_to_png", False):
        png_dst = os.path.splitext(dst_path)[0] + ".png"
        with Image.open(src_path) as im_svg:
            img = im_svg.convert("RGBA")
            img.info['dpi'] = (cfg["dpi"], cfg["dpi"])

            # Detecta categoría y limita tamaño
            cat = _detect_icon_category(src_path)
            max_w, max_h = tuple(cfg["max_size"][cat])
            img.thumbnail((max_w, max_h), Image.LANCZOS)

            # White-wash
            if cfg.get("white_replace"):
                _replace_white(img,
                    tuple(cfg["white_src"]),
                    tuple(cfg["white_dst"])
                )

            img.save(png_dst, "PNG", optimize=True,
                     dpi=(cfg["dpi"], cfg["dpi"]))


def _detect_icon_category(path):
    path_l = path.lower()
    if "group" in path_l:   return "group"
    if "recipe" in path_l:  return "recipe"
    # por defecto
    return next(iter(cfg["max_size"]))

def _replace_white(img, src_rgb, dst_rgb):
    px = img.load()
    w, h = img.size
    for x in range(w):
        for y in range(h):
            if px[x, y][:3] == src_rgb:
                px[x, y] = dst_rgb + (px[x, y][3],)