# Generated by Django 5.1 on 2024-08-25 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digits', models.IntegerField(default=0)),
                ('date', models.DateField(default='null')),
            ],
        ),
    ]
