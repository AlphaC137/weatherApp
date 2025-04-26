from django.contrib import admin
from .models import FavoriteCity

# Register your models here.
@admin.register(FavoriteCity)
class FavoriteCityAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'date_added')
    list_filter = ('user',)
    search_fields = ('name',)
    ordering = ('-date_added',)
