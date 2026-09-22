from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="bill",
            name="paid_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="bill",
            name="payment_method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("cash", "Cash"),
                    ("card", "Card"),
                    ("upi", "UPI"),
                    ("other", "Other"),
                ],
                max_length=20,
            ),
        ),
    ]