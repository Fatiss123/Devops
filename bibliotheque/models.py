from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Livre(models.Model):
    titre = models.CharField(max_length=255)  # Titre du livre
    auteur = models.CharField(max_length=255)  # Auteur du livre
    genre = models.CharField(max_length=100)  # Genre littéraire
    annee_publication = models.PositiveIntegerField()  # Année de publication
    nombre_exemplaires = models.PositiveIntegerField(default=1)  # Nombre d'exemplaires disponibles
    image = models.ImageField(upload_to='images/')  # Chemin vers l'image du livre
    
    def __str__(self):
        return self.titre

    def est_disponible(self):
        """Vérifie si le livre est disponible à l'emprunt."""
        return self.nombre_exemplaires > 0



class Emprunt(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    date_emprunt = models.DateTimeField(auto_now_add=True)  # Ajoute automatiquement la date d'emprunt
    date_rendement = models.DateField()

    def __str__(self):
        return f"Emprunt de {self.livre.titre} par {self.utilisateur.username}"
    

class LivrePerdu(models.Model):
    titre = models.CharField(max_length=255)
    date_signalement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} signalé le {self.date_signalement}"
