from django.shortcuts import render

from .models import DiningTable, MenuCategory, MenuItem


def home(request):
    """
    Public IDDS home page.
    """

    featured_items = (
        MenuItem.objects
        .filter(is_available=True)
        .select_related("category")
        .order_by("category__name", "name")[:6]
    )

    categories = MenuCategory.objects.all().order_by("name")

    return render(
        request,
        "restaurant/home.html",
        {
            "featured_items": featured_items,
            "categories": categories,
        },
    )


def menu(request):
    """
    Customer menu page.
    """

    categories = MenuCategory.objects.prefetch_related(
        "items"
    ).order_by("name")

    items = (
        MenuItem.objects
        .filter(is_available=True)
        .select_related("category")
        .order_by("category__name", "name")
    )

    category_id = request.GET.get("category")

    if category_id:
        items = items.filter(category_id=category_id)

    return render(
        request,
        "restaurant/menu.html",
        {
            "categories": categories,
            "items": items,
            "selected_category": category_id,
        },
    )