# Generated by Django 5.0.2 on 2024-02-11 11:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_password'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='username',
            new_name='nickname',
        ),
    ]
