# Generated by Django 5.0.1 on 2025-05-08 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0004_usuario_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='num_whatsapp',
            field=models.BigIntegerField(),
        ),
    ]
