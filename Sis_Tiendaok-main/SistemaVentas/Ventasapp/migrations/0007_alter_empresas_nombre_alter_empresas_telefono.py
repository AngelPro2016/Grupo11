# Generated by Django 5.1.4 on 2024-12-12 12:56

import Ventasapp.validadores
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ventasapp', '0006_alter_empleados_cedula_alter_empleados_nombre_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresas',
            name='nombre',
            field=models.CharField(max_length=50, validators=[Ventasapp.validadores.validar_cedula], verbose_name='Nombre de la empresa : '),
        ),
        migrations.AlterField(
            model_name='empresas',
            name='telefono',
            field=models.CharField(max_length=10, validators=[Ventasapp.validadores.validar_telefono]),
        ),
    ]
