from PIL import Image, ImageEnhance

def run_transforms(path_or_img, cfg):
    img = path_or_img if isinstance(path_or_img, Image.Image) \
          else Image.open(path_or_img).convert("RGBA")

    if cfg.get("invert"):
        img = Image.eval(img, lambda v: 255-v)
    if cfg.get("adjust_brightness"):
        img = ImageEnhance.Brightness(img).enhance(cfg["brightness_factor"])
    if cfg.get("adjust_contrast"):
        img = ImageEnhance.Contrast(img).enhance(cfg["contrast_factor"])
    if cfg.get("saturate"):
        img = ImageEnhance.Color(img).enhance(cfg["saturation_factor"])

    return img