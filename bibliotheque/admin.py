from django.contrib import admin
from .models import Livre

@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'genre', 'annee_publication', 'nombre_exemplaires')
