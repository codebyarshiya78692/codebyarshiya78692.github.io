from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import DiningTable
from .services import release_table


@login_required
@require_POST
def release_table_view(request, table_id):
    """
    Staff-only endpoint used by the future table-management UI.
    """

    if not request.user.is_staff:
        return JsonResponse(
            {
                "success": False,
                "message": "Staff access is required.",
            },
            status=403,
        )

    table = DiningTable.objects.filter(
        id=table_id
    ).first()

    if table is None:
        return JsonResponse(
            {
                "success": False,
                "message": "Dining table not found.",
            },
            status=404,
        )

    success, message = release_table(table.id)

    table.refresh_from_db()

    return JsonResponse(
        {
            "success": success,
            "message": message,
            "table_id": table.id,
            "table_number": table.table_number,
            "status": table.status,
        },
        status=200 if success else 409,
    )