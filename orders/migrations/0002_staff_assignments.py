from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
        migrations.swappable_dependency(
            settings.AUTH_USER_MODEL,
        ),
    ]

    operations = [

        migrations.AddField(
            model_name="order",
            name="assigned_chef",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={
                    "groups__name": "Chef",
                },
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_orders",
                to=settings.AUTH_USER_MODEL,
            ),
        ),

        migrations.AddField(
            model_name="servicerequest",
            name="assigned_waiter",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={
                    "groups__name": "Waiter",
                },
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_service_requests",
                to=settings.AUTH_USER_MODEL,
            ),
        ),

        migrations.AlterField(
            model_name="servicerequest",
            name="request_type",
            field=models.CharField(
                choices=[
                    ("water", "Water"),
                    ("cutlery", "Cutlery"),
                    ("tissue", "Tissues"),
                    ("assistance", "Assistance"),
                    ("bill", "Bill"),
                    ("other", "Other"),
                ],
                max_length=30,
            ),
        ),
    ]