# Generated by Django 5.1.3 on 2024-11-20 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ventasapp', '0002_alter_clientes_fecha_nacimiento_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clientes',
            options={'verbose_name': 'ingresa los datos del Cliente :', 'verbose_name_plural': 'datos Clientes'},
        ),
        migrations.AlterField(
            model_name='productos',
            name='caracteristicas_categoria',
            field=models.CharField(choices=[('Bebidas', 'Bebidas..'), ('Comidas', 'Comidas'), ('Limpieza', 'Limpieza'), ('Ropa', 'Ropa'), ('Varios', 'Varios')], max_length=100),
        ),
    ]
