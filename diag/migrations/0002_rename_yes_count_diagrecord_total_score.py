# Generated by Django 4.2.9 on 2024-07-28 12:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diag', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='diagrecord',
            old_name='yes_count',
            new_name='total_score',
        ),
    ]
