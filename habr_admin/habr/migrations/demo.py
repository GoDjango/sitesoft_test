import logging
from django.db import migrations

_logger = logging.getLogger(__name__)

def fill_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User(password='pbkdf2_sha256$216000$FZONeAsCA8AN$KNms/LzcG4pmDytpfccaI8nEkfZxM6Imr3YU3YWlZZ4=',
         is_superuser=True,
         is_staff=True,
         is_active=True,
         username='admin',
         email='admin@example.com',
         ).save()

def fill_hubs(apps, schema_editor):
    Hub = apps.get_model('habr', 'Hub')

    Hub(name='Карьера в IT-индустрии',
        url='https://habr.com/ru/hub/career/',
        period=3,
        ).save()
    Hub(name='DIY или Сделай сам',
        url='https://habr.com/ru/hub/DIY/',
        period=2,
        ).save()
    Hub(name='Управление персоналом',
        url='https://habr.com/ru/hub/hr_management/',
        period=5,
        ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('habr', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fill_user),
        migrations.RunPython(fill_hubs),
    ]
