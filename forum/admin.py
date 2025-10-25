from django.contrib import admin
from .models import Club

#@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'league', 'founded_year']
    list_filter = ['league', 'name']
    search_fields = ['name', 'league']