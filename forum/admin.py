from django.contrib import admin
from .models import Club

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['club_name', 'league', 'region', 'year_founded']
    list_filter = ['league', 'region']
    search_fields = ['club_name', 'league']