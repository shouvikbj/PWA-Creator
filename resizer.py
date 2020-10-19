import PIL
import os
from PIL import Image

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def resize(width,height,email,project,image):
    img = Image.open(f"{APP_ROOT}/static/folders/{email}/{project}/{image}")
    img = img.resize((width, height),PIL.Image.ANTIALIAS)
    filename = f"logo{str(width)}.png"
    img.save(f"{APP_ROOT}/static/folders/{email}/{project}/{filename}")