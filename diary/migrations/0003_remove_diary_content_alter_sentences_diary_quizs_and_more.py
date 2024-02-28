# Generated by Django 5.0.2 on 2024-02-28 12:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0002_sentences_keyword'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diary',
            name='content',
        ),
        migrations.AlterField(
            model_name='sentences',
            name='diary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sentences', to='diary.diary'),
        ),
        migrations.CreateModel(
            name='Quizs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.TextField()),
                ('answer', models.CharField(max_length=50)),
                ('sentence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizs', to='diary.sentences')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Keyword',
        ),
    ]