# Generated by Django 5.1 on 2024-08-08 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='cc',
            field=models.IntegerField(default=0, unique=True),
        ),
    ]
