from django.db import transaction

from orders.models import DiningSession

from .models import DiningTable


@transaction.atomic
def release_table(table_id):
    """
    Safely release a dining table.

    A table with an active dining session cannot be manually
    released. The normal billing workflow must complete the
    session first.
    """

    table = (
        DiningTable.objects
        .select_for_update()
        .get(id=table_id)
    )

    active_session = (
        DiningSession.objects
        .filter(
            table=table,
            status="active",
        )
        .first()
    )

    if active_session:
        return (
            False,
            (
                f"Table {table.table_number} cannot be released. "
                "It still has an active dining session. "
                "Complete the bill first."
            ),
        )

    table.status = "available"
    table.save(update_fields=["status"])

    return (
        True,
        f"Table {table.table_number} is now available.",
    )