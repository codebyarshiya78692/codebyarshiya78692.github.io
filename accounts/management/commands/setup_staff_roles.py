from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User


class Command(BaseCommand):
    help = "Create IDDS Chef and Waiter staff roles and demo accounts."


    def handle(self, *args, **options):

        # =====================================================
        # GROUPS
        # =====================================================

        chef_group, _ = Group.objects.get_or_create(
            name="Chef"
        )

        waiter_group, _ = Group.objects.get_or_create(
            name="Waiter"
        )


        # =====================================================
        # CHEF ACCOUNT
        # =====================================================

        chef, chef_created = User.objects.get_or_create(
            username="chef"
        )

        if chef_created:

            chef.set_password(
                "Chef@12345"
            )

            chef.first_name = "Kitchen"
            chef.last_name = "Chef"
            chef.is_staff = True
            chef.is_active = True

            chef.save()

        chef.groups.add(
            chef_group
        )


        # =====================================================
        # WAITER ACCOUNT
        # =====================================================

        waiter, waiter_created = User.objects.get_or_create(
            username="waiter"
        )

        if waiter_created:

            waiter.set_password(
                "Waiter@12345"
            )

            waiter.first_name = "Restaurant"
            waiter.last_name = "Waiter"
            waiter.is_staff = True
            waiter.is_active = True

            waiter.save()

        waiter.groups.add(
            waiter_group
        )


        # =====================================================
        # OUTPUT
        # =====================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "IDDS STAFF ROLES READY"
            )
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
            "  URL: /accounts/chef/login/"
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
            "  URL: /accounts/waiter/login/"
        )

        self.stdout.write("")

        if not chef_created:
            self.stdout.write(
                self.style.WARNING(
                    "Existing 'chef' account was kept; its password was not changed."
                )
            )

        if not waiter_created:
            self.stdout.write(
                self.style.WARNING(
                    "Existing 'waiter' account was kept; its password was not changed."
                )
            )

        self.stdout.write("")