# Generated by Django 5.0.4 on 2024-04-13 17:15

import prefix_id.field
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="id",
            field=prefix_id.field.PrefixIDField(
                editable=False,
                max_length=27,
                prefix="user",
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
