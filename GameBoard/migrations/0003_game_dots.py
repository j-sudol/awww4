# Generated by Django 4.2 on 2025-05-19 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GameBoard', '0002_alter_board_dots_game'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='dots',
            field=models.JSONField(default=list),
        ),
    ]
