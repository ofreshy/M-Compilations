# Generated by Django 5.1 on 2024-08-19 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musik_lib', '0004_alter_artist_id_alter_artistfrequencycollection_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='ordinal',
            field=models.PositiveSmallIntegerField(null=True, unique=True),
        ),
    ]
