import os
import cv2
import numpy as np
from PIL import Image
from cv2 import dnn_superres
from urllib.request import urlretrieve
from tempfile import NamedTemporaryFile

# Configuración del modelo
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_NAME = "FSRCNN_x2.pb"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)
MODEL_URL = (
    "https://raw.githubusercontent.com/Saafke/FSRCNN_Tensorflow/"
    "master/models/FSRCNN_x2.pb"
)


def _download_model():
    """
    Descarga el modelo FSRCNN_x2 de forma segura.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    tmp = NamedTemporaryFile(delete=False, dir=MODEL_DIR, suffix=".tmp")
    try:
        urlretrieve(MODEL_URL, tmp.name)
        os.replace(tmp.name, MODEL_PATH)
    finally:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)


def _ensure_model():
    """
    Verifica que el modelo exista, si no, lo descarga.
    """
    if not os.path.isfile(MODEL_PATH):
        _download_model()


def upscale(img: Image.Image) -> Image.Image:
    """
    Aplica super-resolución FSRCNN_x2 a una imagen PIL con canal alfa.
    - Descarga el modelo si hace falta.
    - Convierte PIL→OpenCV, aplica upscale a RGB, reajusta canal alfa, y vuelve a PIL.
    """
    _ensure_model()

    # Convertir PIL a array numpy
    img_np = np.array(img)
    if img_np.ndim != 3 or img_np.shape[2] not in (3, 4):
        raise ValueError("Imagen debe tener 3 o 4 canales (RGB o RGBA)")

    # Separar canales
    if img_np.shape[2] == 4:
        rgb = img_np[..., :3]
        alpha = img_np[..., 3]
    else:
        rgb = img_np
        alpha = None

    # RGB a BGR para OpenCV
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    # Cargar modelo
    sr = dnn_superres.DnnSuperResImpl_create()
    sr.readModel(MODEL_PATH)
    sr.setModel("fsrcnn", 2)

    # Aplicar upscale
    up_bgr = sr.upsample(bgr)

    # BGR a RGB
    up_rgb = cv2.cvtColor(up_bgr, cv2.COLOR_BGR2RGB)

    # Ajustar canal alfa si existe
    if alpha is not None:
        # Redimensionar alfa con nearest neighbor
        h, w = up_rgb.shape[:2]
        up_alpha = cv2.resize(alpha, (w, h), interpolation=cv2.INTER_NEAREST)
        # Combinar
        up_rgba = np.dstack((up_rgb, up_alpha))
        result = Image.fromarray(up_rgba, mode="RGBA")
    else:
        result = Image.fromarray(up_rgb, mode="RGB")

    return result
