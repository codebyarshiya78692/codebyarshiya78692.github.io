from django.contrib.auth.models import Group


CHEF_GROUP = "Chef"
WAITER_GROUP = "Waiter"


def is_chef(user):
    """
    Return True when the user belongs to the Chef group.
    """

    if not user.is_authenticated:
        return False

    return user.groups.filter(
        name=CHEF_GROUP
    ).exists()


def is_waiter(user):
    """
    Return True when the user belongs to the Waiter group.
    """

    if not user.is_authenticated:
        return False

    return user.groups.filter(
        name=WAITER_GROUP
    ).exists()


def is_restaurant_staff(user):
    """
    Restaurant operational staff are Chefs or Waiters.
    """

    return is_chef(user) or is_waiter(user)


def is_admin_user(user):
    """
    Django administrators are handled separately.
    """

    return (
        user.is_authenticated
        and user.is_staff
        and not is_chef(user)
        and not is_waiter(user)
    )