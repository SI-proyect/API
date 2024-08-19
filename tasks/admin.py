from django.contrib import admin
from .models import User, Client
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email",)


class CustomUserAdmin(UserAdmin):
    """
    Class to customize the user administration panel
    """

    model = User
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = (
            "id",
            "cc",
            "email",
            "name",
            "last_name",
            "created_at",
            "is_staff",
            "is_active",
        )
    list_filter = (
        "is_staff",
        "is_active",
    )
    fieldsets = (
        ("Information", {"fields": ("email", "password", "last_name")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "cc",
                    "email",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("email", "name", "last_name")
    ordering = ("id",)


class ClientAdmin(admin.ModelAdmin):
    list_display = (
            "id",
            "cc",
            "nit",
            "name",
            "address",
            "telephone",
            "mail",
            "user",
            "notes",
            "fiscal_responsibilities"
    )

    search_fields = ("cc", "nit", "mail")


admin.site.register(Client, ClientAdmin)
admin.site.register(User, CustomUserAdmin)