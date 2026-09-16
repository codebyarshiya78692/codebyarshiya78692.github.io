from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from restaurant.views import (
    add_to_cart,
    cart,
    home,
    menu,
    order_confirmation,
    order_tracking,
    place_order,
    start_dining,
    table_selection,
    update_cart,
)


# ============================================================
# DJANGO ADMIN BRANDING
# ============================================================

admin.site.site_header = "IDDS Administration"
admin.site.site_title = "IDDS Admin"
admin.site.index_title = "Integrated Digital Dining System"


# ============================================================
# MAIN URL CONFIGURATION
# ============================================================

urlpatterns = [

    # --------------------------------------------------------
    # CUSTOMER HOME
    # --------------------------------------------------------

    path(
        "",
        home,
        name="home",
    ),


    # --------------------------------------------------------
    # DJANGO ADMIN
    # --------------------------------------------------------

    path(
        "admin/",
        admin.site.urls,
    ),


    # --------------------------------------------------------
    # ACCOUNTS
    # --------------------------------------------------------

    path(
        "",
        include("accounts.urls"),
    ),


    # --------------------------------------------------------
    # CUSTOMER DINING FLOW
    # --------------------------------------------------------

    # Select a dining table
    path(
        "tables/",
        table_selection,
        name="table_selection",
    ),

    # Start a dining session
    path(
        "dining/start/<int:table_id>/",
        start_dining,
        name="start_dining",
    ),

    # View menu for selected table
    path(
        "menu/<int:table_id>/",
        menu,
        name="menu",
    ),


    # --------------------------------------------------------
    # CUSTOMER CART
    # --------------------------------------------------------

    path(
        "cart/",
        cart,
        name="cart",
    ),

    path(
        "cart/add/<int:item_id>/",
        add_to_cart,
        name="add_to_cart",
    ),

    path(
        "cart/update/<int:item_id>/",
        update_cart,
        name="update_cart",
    ),


    # --------------------------------------------------------
    # CUSTOMER ORDERS
    # --------------------------------------------------------

    path(
        "order/place/",
        place_order,
        name="place_order",
    ),

    path(
        "order/<int:order_id>/confirmation/",
        order_confirmation,
        name="order_confirmation",
    ),

    path(
        "order/<int:order_id>/track/",
        order_tracking,
        name="order_tracking",
    ),


    # --------------------------------------------------------
    # KITCHEN / CHEF
    # --------------------------------------------------------

    path(
        "kitchen/",
        include(
            (
                "kitchen.urls",
                "kitchen",
            ),
            namespace="kitchen",
        ),
    ),


    # --------------------------------------------------------
    # BILLING
    # --------------------------------------------------------

    path(
        "billing/",
        include("billing.urls"),
    ),


    # --------------------------------------------------------
    # REPORTS
    # --------------------------------------------------------

    path(
        "reports/",
        include("reports.urls"),
    ),
]


# ============================================================
# MEDIA FILES
# ============================================================
#
# Used for uploaded food/menu images during development.
#
# Example:
# /media/menu/cappuccino.jpg
#
# Production deployment should serve media separately.
# ============================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )