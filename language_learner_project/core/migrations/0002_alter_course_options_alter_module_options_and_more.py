# Generated by Django 5.2 on 2025-04-26 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="course",
            options={
                "ordering": ["created_at"],
                "verbose_name": "Kurs",
                "verbose_name_plural": "Kurser",
            },
        ),
        migrations.AlterModelOptions(
            name="module",
            options={
                "ordering": ["order"],
                "verbose_name": "Modul",
                "verbose_name_plural": "Moduler",
            },
        ),
        migrations.AlterModelOptions(
            name="sentence",
            options={
                "ordering": ["order"],
                "verbose_name": "Mening",
                "verbose_name_plural": "Meningar",
            },
        ),
        migrations.AlterModelOptions(
            name="word",
            options={"verbose_name": "Ord", "verbose_name_plural": "Ord"},
        ),
        migrations.AlterField(
            model_name="module",
            name="description",
            field=models.TextField(blank=True, max_length=8000),
        ),
        migrations.AlterField(
            model_name="module",
            name="text",
            field=models.TextField(blank=True, max_length=8000),
        ),
    ]
