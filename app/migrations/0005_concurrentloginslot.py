from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_login_slots(apps, schema_editor):
    ConcurrentLoginSlot = apps.get_model('app', 'ConcurrentLoginSlot')
    ConcurrentLoginSlot.objects.bulk_create([
        ConcurrentLoginSlot(slot_number=slot_number)
        for slot_number in range(1, 11)
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_favorite'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConcurrentLoginSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot_number', models.PositiveSmallIntegerField(unique=True)),
                ('session_key', models.CharField(blank=True, max_length=40, null=True, unique=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='concurrent_login_slots', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['slot_number'],
            },
        ),
        migrations.RunPython(create_login_slots, migrations.RunPython.noop),
    ]
