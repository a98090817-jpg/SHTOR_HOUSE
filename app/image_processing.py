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

# Brauzerlar bevosita ko'rsata oladigan rasm formatlari.
# Boshqa formatlar (HEIC/HEIF va h.k.) bazaga saqlashdan oldin WEBP ga o'giriladi.
BROWSER_SAFE_IMAGE_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/gif',
}


def convert_to_webp(uploaded_image):
    """Har qanday rasmni brauzer ko'rsata oladigan WEBP ga o'giradi."""
    with Image.open(uploaded_image) as opened_image:
        image = ImageOps.exif_transpose(opened_image)
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGBA')
        if image.mode == 'RGBA':
            matte = Image.new('RGB', image.size, '#eee8df')
            matte.paste(image, mask=image.getchannel('A'))
            image = matte
        output = BytesIO()
        image.save(output, format='WEBP', quality=90, method=6)
    converted = ContentFile(output.getvalue())
    converted.name = f'{Path(uploaded_image.name).stem}.webp'
    return converted


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
