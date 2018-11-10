import os

from PIL import Image

from django.core.cache import cache

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def add_watermark(input_image_path, output_image_path):
    watermark = os.path.join(BASE_DIR, 'watermark.png')
    base_image = Image.open(input_image_path)
    watermark = Image.open(watermark)
    width, height = base_image.size
    w_width, w_height = watermark.size

    base_image.paste(watermark, (width-w_width, height-w_height), watermark)
    base_image.save(output_image_path)
