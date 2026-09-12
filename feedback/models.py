from django.db import models

from orders.models import DiningSession


class Feedback(models.Model):
    RATING_CHOICES = [
        (1, "1 - Very Poor"),
        (2, "2 - Poor"),
        (3, "3 - Average"),
        (4, "4 - Good"),
        (5, "5 - Excellent"),
    ]

    session = models.OneToOneField(
        DiningSession,
        on_delete=models.CASCADE,
        related_name="feedback",
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
    )

    comment = models.TextField(
        blank=True,
    )

    would_recommend = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"Feedback - Table "
            f"{self.session.table.table_number} - "
            f"{self.rating}/5"
        )