# Generated by Django 4.2.9 on 2024-07-27 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_pass_word_user_password_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DiagRecord',
        ),
    ]
