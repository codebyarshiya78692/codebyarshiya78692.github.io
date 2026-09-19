from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from orders.models import DiningSession, ServiceRequest


# ============================================================
# CUSTOMER SESSION
# ============================================================

def _get_customer_session(request):
    """
    Return the active dining session belonging to the current
    browser session.

    Customers using the restaurant's QR/table flow are identified
    through the dining_session_id stored in Django's session.
    """

    session_id = request.session.get("dining_session_id")

    if not session_id:
        return None

    return (
        DiningSession.objects
        .select_related("table")
        .filter(
            id=session_id,
            status="active",
        )
        .first()
    )


# ============================================================
# STAFF ROLE
# ============================================================

def _staff_role(request):
    """
    Identify the operational role of the current user.

    Roles:
        admin
        chef
        waiter
        staff
        anonymous
    """

    user = request.user

    if not user.is_authenticated:
        return "anonymous"

    if user.is_superuser:
        return "admin"

    if user.groups.filter(
        name__iexact="Chef"
    ).exists():
        return "chef"

    if user.groups.filter(
        name__iexact="Waiter"
    ).exists():
        return "waiter"

    return "staff"


def _staff_only(request):
    """
    Return True when the current user is an authenticated
    staff member.
    """

    return (
        request.user.is_authenticated
        and request.user.is_staff
    )


def _allowed_request_types(request):
    """
    Return the service-request types visible to each role.

    Admin:
        Everything

    Chef:
        Food/custom requests only

    Waiter:
        Water, cutlery and bill only

    Other staff:
        No operational service requests
    """

    role = _staff_role(request)

    if role == "admin":
        return [
            "water",
            "cutlery",
            "assistance",
            "bill",
            "other",
        ]

    if role == "chef":
        return [
            "assistance",
            "other",
        ]

    if role == "waiter":
        return [
            "water",
            "cutlery",
            "bill",
        ]

    return []


# ============================================================
# ACCESS DENIED
# ============================================================

def _staff_access_denied(request):
    """
    Render a consistent access-denied page for non-staff users.
    """

    return render(
        request,
        "restaurant/access_denied.html",
        status=403,
    )


# ============================================================
# CUSTOMER SERVICE REQUEST PAGE
# ============================================================

def service_requests(request):
    """
    Customer service-request page.

    Customers can request:
        - Water
        - Cutlery
        - Assistance
        - Bill
        - Other

    Staff members are shown only the requests appropriate
    for their role.
    """

    if (
        request.user.is_authenticated
        and request.user.is_staff
    ):
        return staff_service_requests(request)

    dining_session = _get_customer_session(request)

    if dining_session is None:
        messages.error(
            request,
            "Please select a table before requesting service.",
        )

        return redirect("table_selection")

    requests = (
        ServiceRequest.objects
        .filter(
            session=dining_session,
        )
        .select_related(
            "session",
            "session__table",
        )
        .order_by(
            "-requested_at",
        )
    )

    return render(
        request,
        "restaurant/service_requests.html",
        {
            "session": dining_session,
            "table": dining_session.table,
            "service_requests": requests,
        },
    )


# ============================================================
# CREATE CUSTOMER SERVICE REQUEST
# ============================================================

def create_service_request(request):
    """
    Create a new service request for the customer's active
    dining session.
    """

    if request.method != "POST":
        return redirect("service_requests")

    dining_session = _get_customer_session(request)

    if dining_session is None:
        messages.error(
            request,
            "Your dining session is no longer active.",
        )

        return redirect("table_selection")

    request_type = request.POST.get(
        "request_type",
        "",
    ).strip()

    message = request.POST.get(
        "message",
        "",
    ).strip()

    valid_request_types = {
        choice[0]
        for choice in ServiceRequest.REQUEST_TYPES
    }

    if request_type not in valid_request_types:
        messages.error(
            request,
            "Please select a valid service request.",
        )

        return redirect("service_requests")

    # Prevent accidentally creating many identical
    # open requests.
    existing_request = (
        ServiceRequest.objects
        .filter(
            session=dining_session,
            request_type=request_type,
            status__in=[
                "requested",
                "accepted",
            ],
        )
        .first()
    )

    if existing_request:
        messages.info(
            request,
            "You already have an active request of this type.",
        )

        return redirect("service_requests")

    ServiceRequest.objects.create(
        session=dining_session,
        request_type=request_type,
        message=message,
        status="requested",
    )

    messages.success(
        request,
        "Your service request has been sent to the staff.",
    )

    return redirect("service_requests")


# ============================================================
# STAFF SERVICE REQUEST DASHBOARD
# ============================================================

@login_required
def staff_service_requests(request):
    """
    Staff dashboard for incoming customer service requests.

    Visibility is role-specific.

    Admin:
        All requests

    Chef:
        Assistance and Other

    Waiter:
        Water, Cutlery and Bill
    """

    if not _staff_only(request):
        return _staff_access_denied(request)

    allowed_types = _allowed_request_types(request)

    # If the user is staff but does not have a recognised
    # operational role, do not expose customer requests.
    if not allowed_types:
        return _staff_access_denied(request)

    service_request_list = (
        ServiceRequest.objects
        .filter(
            request_type__in=allowed_types,
        )
        .select_related(
            "session",
            "session__table",
        )
        .order_by(
            "-requested_at",
        )
    )

    requested_requests = service_request_list.filter(
        status="requested",
    )

    accepted_requests = service_request_list.filter(
        status="accepted",
    )

    completed_requests = service_request_list.filter(
        status="completed",
    )

    return render(
        request,
        "restaurant/service_requests_staff.html",
        {
            "service_requests": service_request_list,
            "requested_requests": requested_requests,
            "accepted_requests": accepted_requests,
            "completed_requests": completed_requests,
            "requested_count": requested_requests.count(),
            "accepted_count": accepted_requests.count(),
            "completed_count": completed_requests.count(),
        },
    )


# ============================================================
# ACCEPT SERVICE REQUEST
# ============================================================

@login_required
def accept_service_request(request, request_id):
    """
    Staff accepts an incoming service request.

    The request must belong to the types allowed for the
    current staff role.
    """

    if not _staff_only(request):
        return _staff_access_denied(request)

    if request.method != "POST":
        return redirect("staff_service_requests")

    allowed_types = _allowed_request_types(request)

    if not allowed_types:
        return _staff_access_denied(request)

    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            "session",
            "session__table",
        ),
        id=request_id,
        request_type__in=allowed_types,
    )

    if service_request.status != "requested":
        messages.info(
            request,
            "This service request is no longer waiting "
            "for acceptance.",
        )

        return redirect("staff_service_requests")

    service_request.status = "accepted"

    service_request.save(
        update_fields=[
            "status",
        ],
    )

    messages.success(
        request,
        (
            f"Request for Table "
            f"{service_request.session.table.table_number} "
            "has been accepted."
        ),
    )

    return redirect("staff_service_requests")
# ============================================================
# COMPLETE SERVICE REQUEST
# ============================================================

@login_required
def complete_service_request(request, request_id):
    """
    Staff completes an accepted service request.

    Only requests belonging to the current user's role
    can be completed.
    """

    if not _staff_only(request):
        return _staff_access_denied(request)

    if request.method != "POST":
        return redirect("staff_service_requests")

    allowed_types = _allowed_request_types(request)

    if not allowed_types:
        return _staff_access_denied(request)

    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            "session",
            "session__table",
        ),
        id=request_id,
        request_type__in=allowed_types,
    )

    if service_request.status != "accepted":
        messages.info(
            request,
            "Only accepted service requests can be completed.",
        )

        return redirect("staff_service_requests")

    service_request.status = "completed"
    service_request.completed_at = timezone.now()

    service_request.save(
        update_fields=[
            "status",
            "completed_at",
        ],
    )

    messages.success(
        request,
        (
            f"Service request for Table "
            f"{service_request.session.table.table_number} "
            "has been completed."
        ),
    )

    return redirect("staff_service_requests")


# ============================================================
# SERVICE REQUEST DETAIL
# ============================================================

@login_required
def staff_service_request_detail(request, request_id):
    """
    Staff-only detail page for one service request.

    The request must belong to the current user's allowed
    request types.
    """

    if not _staff_only(request):
        return _staff_access_denied(request)

    allowed_types = _allowed_request_types(request)

    if not allowed_types:
        return _staff_access_denied(request)

    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            "session",
            "session__table",
        ),
        id=request_id,
        request_type__in=allowed_types,
    )

    return render(
        request,
        "restaurant/service_request_detail.html",
        {
            "service_request": service_request,
        },
    )