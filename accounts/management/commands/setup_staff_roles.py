from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = (
        "Create IDDS Chef and Waiter groups and reset "
        "the standard demo staff accounts."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        chef_group, _ = Group.objects.get_or_create(
            name="Chef",
        )

        waiter_group, _ = Group.objects.get_or_create(
            name="Waiter",
        )

        # =====================================================
        # CHEF
        # =====================================================

        chef, chef_created = User.objects.get_or_create(
            username="chef",
        )

        chef.set_password(
            "Chef@12345",
        )

        chef.first_name = "Kitchen"
        chef.last_name = "Chef"
        chef.is_staff = True
        chef.is_active = True

        chef.save()

        chef.groups.add(
            chef_group,
        )

        # =====================================================
        # WAITER
        # =====================================================

        waiter, waiter_created = User.objects.get_or_create(
            username="waiter",
        )

        waiter.set_password(
            "Waiter@12345",
        )

        waiter.first_name = "Restaurant"
        waiter.last_name = "Waiter"
        waiter.is_staff = True
        waiter.is_active = True

        waiter.save()

        waiter.groups.add(
            waiter_group,
        )

        # =====================================================
        # OUTPUT
        # =====================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "IDDS STAFF ROLES READY",
            )
        )

        self.stdout.write("")

        self.stdout.write(
            "Unified staff login:"
        )

        self.stdout.write(
            "  URL: /accounts/login/"
        )

        self.stdout.write("")

        self.stdout.write(
            "Chef login:"
        )

        self.stdout.write(
            "  Username: chef"
        )

        self.stdout.write(
            "  Password: Chef@12345"
        )

        self.stdout.write(
            "  Redirect: Kitchen Dashboard"
        )

        self.stdout.write("")

        self.stdout.write(
            "Waiter login:"
        )

        self.stdout.write(
            "  Username: waiter"
        )

        self.stdout.write(
            "  Password: Waiter@12345"
        )

        self.stdout.write(
            "  Redirect: Waiter Dashboard"
        )

        self.stdout.write("")

        if not chef_created:

            self.stdout.write(
                self.style.WARNING(
                    "Existing 'chef' account found; "
                    "its password has been reset to "
                    "Chef@12345.",
                )
            )

        if not waiter_created:

            self.stdout.write(
                self.style.WARNING(
                    "Existing 'waiter' account found; "
                    "its password has been reset to "
                    "Waiter@12345.",
                )
            )

        self.stdout.write("")