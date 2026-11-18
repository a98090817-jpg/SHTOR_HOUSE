from django.core.management.base import BaseCommand

from app.models import Product


class Command(BaseCommand):
    help = (
        'Diskda hali saqlanib turgan mahsulot rasmlarini bazaga nusxalaydi. '
        'Deploydan keyin bir marta ishga tushiring: python manage.py backfill_product_images'
    )

    def handle(self, *args, **options):
        updated = 0
        skipped = 0
        for product in Product.objects.exclude(image='').exclude(image__isnull=True):
            had_data = bool(product.image_data)
            product.save()
            if product.image_data and not had_data:
                updated += 1
            elif not product.image_data:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'{updated} ta rasm bazaga nusxalandi, '
                f'{skipped} ta rasm fayli topilmadi.'
            )
        )
        if skipped:
            self.stdout.write(
                self.style.WARNING(
                    'Fayli yo\'qolgan mahsulotlarga rasmni saytdan qayta yuklang.'
                )
            )
