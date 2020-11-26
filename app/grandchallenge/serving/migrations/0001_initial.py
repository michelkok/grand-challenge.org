# Generated by Django 3.0.5 on 2020-05-24 17:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cases", "0023_auto_20200521_1052"),
        ("evaluation", "0001_squashed_0010_auto_20201121_1348"),
    ]

    operations = [
        migrations.CreateModel(
            name="Download",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("count", models.BigIntegerField(default=1)),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cases.Image",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="evaluation.Submission",
                    ),
                ),
            ],
            options={"unique_together": {("creator", "image", "submission")}},
        ),
    ]