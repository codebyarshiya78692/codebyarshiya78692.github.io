from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("restaurant", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="menuitem",
            name="image_url",
            field=models.URLField(
                blank=True,
                help_text="External image URL displayed on the digital menu.",
                max_length=500,
            ),
        ),
    ]