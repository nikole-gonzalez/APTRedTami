# Generated by Django 5.0.1 on 2025-05-13 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0007_alter_perfilusuario_usuario_sist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilusuario',
            name='cod_acceso',
            field=models.CharField(default='', max_length=50),
        ),
    ]
