from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.expressions import result

from .models import User, Post, Contact, Image

admin.sites.AdminSite.site_header = "پنل مدیریت جنگو"
admin.sites.AdminSite.site_title = "پنل"
admin.sites.AdminSite.index_title = "پنل مدیریت"


# action for Post models
def make_deactivation(modeladmin, request, queryset):
    results = queryset.update(active=False)
    modeladmin.message_user(request, f"{results} posts were rejected")


make_deactivation.short_description = "رد پست"


def make_activation(modeladmin, request, queryset):
    results = queryset.update(active=True)
    modeladmin.message_user(request, f"{results} posts were accepted")


make_activation.short_description = "تایید پست"


# Register your models here.

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'phone']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('date_of_birth', 'bio', 'photo', 'job', 'phone')}),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'created', 'description']
    ordering = ['created']
    search_fields = ['description']
    actions = [make_deactivation, make_activation]


admin.site.register(Contact)
admin.site.register(Image)
