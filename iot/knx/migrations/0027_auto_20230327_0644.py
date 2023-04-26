# Generated by Django 3.2.18 on 2023-03-27 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0026_auto_20230324_0850'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='functionkeyledsubscriptions',
            name='fkey_no',
        ),
        migrations.AlterField(
            model_name='functionkeyledsubscriptions',
            name='phone_model',
            field=models.CharField(choices=[('D335', 'D335'), ('D385', 'D385'), ('D713', 'D713'), ('D717', 'D717'), ('D735', 'D735'), ('D785', 'D785'), ('D862', 'D862'), ('D865', 'D865')], max_length=4, null=True),
        ),
    ]