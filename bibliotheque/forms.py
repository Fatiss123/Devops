from django import forms
from .models import Livre
from .models import LivrePerdu  # Modèle à créer

class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = ['titre', 'auteur', 'genre', 'annee_publication', 'nombre_exemplaires', 'image']


class LivrePerduForm(forms.ModelForm):
    class Meta:
        model = LivrePerdu
        fields = ['titre']  # Seulement 'titre' est défini dans le modèle
