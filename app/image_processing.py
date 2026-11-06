from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

try:
    from pillow_heif import register_heif_opener
except ImportError:  # HEIC qo'llab-quvvatlash paketi o'rnatilmagan bo'lsa ham sayt ishlaydi
    register_heif_opener = None
else:
    register_heif_opener()


PRODUCT_IMAGE_SIZE = (1200, 1500)


def normalize_product_image(uploaded_image):
    with Image.open(uploaded_image) as opened_image:
        source = ImageOps.exif_transpose(opened_image).convert('RGBA')

    matte = Image.new('RGB', source.size, '#eee8df')
    matte.paste(source, mask=source.getchannel('A'))
    background = ImageOps.fit(
        matte,
        PRODUCT_IMAGE_SIZE,
        method=Image.Resampling.LANCZOS,
    )
    background = ImageEnhance.Brightness(
        background.filter(ImageFilter.GaussianBlur(radius=32))
    ).enhance(0.72)

    foreground = ImageOps.contain(
        source,
        PRODUCT_IMAGE_SIZE,
        method=Image.Resampling.LANCZOS,
    )
    left = (PRODUCT_IMAGE_SIZE[0] - foreground.width) // 2
    top = (PRODUCT_IMAGE_SIZE[1] - foreground.height) // 2
    background.paste(foreground, (left, top), mask=foreground.getchannel('A'))

    output = BytesIO()
    background.save(output, format='WEBP', quality=88, method=6)
    normalized_image = ContentFile(output.getvalue())
    normalized_image.name = f'{Path(uploaded_image.name).stem}.webp'
    return normalized_image
