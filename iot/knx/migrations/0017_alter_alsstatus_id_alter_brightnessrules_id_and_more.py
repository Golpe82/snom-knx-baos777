# Generated by Django 4.0.4 on 2022-09-20 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0016_auto_20210913_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alsstatus',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='brightnessrules',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='knxmonitor',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='knxstatus',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]