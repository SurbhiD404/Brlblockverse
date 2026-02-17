from django.contrib import admin
from .models import Team, Player

class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("team_id", "team_type", "created_at")
    inlines = [PlayerInline]

@admin.register(Player)             
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "student_no", "email", "branch","year", "team")
    search_fields = ("name", "student_no", "email")
    list_filter = ("attendance", "branch", "year")