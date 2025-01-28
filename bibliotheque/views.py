from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Livre, Emprunt  # Remplacez par votre modèle approprié
from .forms import LivreForm
from django.contrib.auth import logout
from django.http import JsonResponse
from .forms import LivrePerduForm, LivrePerdu  # Formulaire à créer
from datetime import datetime
from datetime import date
from django.utils import timezone

from django.views.decorators.cache import never_cache

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Récupérer l'utilisateur avec l'email
        user = User.objects.filter(email=email).first()
        if user:
            # Authentifier avec le username et le mot de passe
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('accueil')  # Redirige vers la page d'accueil
        messages.error(request, 'Email ou mot de passe incorrect.')

    return render(request, 'bibliotheque/login.html')



def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nom d\'utilisateur déjà pris.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
        else:
            # Créer le nouvel utilisateur
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Compte créé avec succès. Connectez-vous.')
            return redirect('login')

    return render(request, 'bibliotheque/signup.html')


# Vue pour la déconnexion
def logout_view(request):
    logout(request)  # Déconnecte l'utilisateur actuel
    return redirect('login')  # Redirige l'utilisateur vers la page de connexion


@never_cache
def accueil_view(request):
    if not request.user.is_authenticated:
        # Ajoutez un message d'erreur si l'utilisateur n'est pas connecté
        messages.error(request, "Connectez-vous d'abord pour accéder à cette page.")
        return redirect('login')  # Redirige vers la page de connexion

    # Si l'utilisateur est connecté, récupérez les données nécessaires
    livres = Livre.objects.all()  # Récupère tous les livres
    emprunts = Emprunt.objects.filter(utilisateur=request.user)  # Récupère les emprunts pour l'utilisateur connecté
    emprunts_ids = [emprunt.livre.id for emprunt in emprunts]  # Récupère les IDs des livres empruntés

    return render(request, 'bibliotheque/accueil.html', {'livres': livres, 'emprunts_ids': emprunts_ids})


@login_required
def rechercher_livre(request):
    query = request.GET.get('q', '').strip()
    livres = Livre.objects.filter(titre__icontains=query)
    data = {
        'livres': [
            {
                'titre': livre.titre,
                'auteur': livre.auteur,
                'genre': livre.genre,
                'annee_publication': livre.annee_publication,
                'image': livre.image.url,
            }
            for livre in livres
        ]
    }
    return JsonResponse(data)


# Ajouter un livre
def add_livre(request):
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('list_livres')  # Redirection vers la liste des livres après l'ajout
    else:
        form = LivreForm()
    return render(request, 'bibliotheque/add_livre.html', {'form': form})

# Afficher tous les livres
def list_livres(request):
    livres = Livre.objects.all()
    return render(request, 'bibliotheque/list_livres.html', {'livres': livres})


@login_required
def emprunter_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    date_actuelle = date.today()

    if request.method == "POST":
        titre = request.POST.get("titre")  # Le titre du livre saisi par l'utilisateur
        email = request.POST.get("email")
        telephone = request.POST.get("telephone")
        date_rendement_str = request.POST.get("date_rendement")

        # Vérification si le livre existe dans la base de données
        livre = Livre.objects.filter(titre__iexact=titre).first()  # Recherche sans tenir compte de la casse

        if not livre:
            messages.error(request, "Le livre avec ce titre n'existe pas.")
            return redirect("emprunter_livre", livre_id=livre_id)  # Redirection avec l'ID du livre

        # Calculer le nombre d'exemplaires disponibles
        emprunts_en_cours = Emprunt.objects.filter(livre=livre, date_rendement__gte=date_actuelle).count()
        exemplaires_disponibles = livre.nombre_exemplaires - emprunts_en_cours

        if exemplaires_disponibles <= 0:
            messages.error(request, "Le livre sélectionné n'est plus disponible.")
            return redirect("emprunter_livre", livre_id=livre_id)  # Redirection avec l'ID du livre

        # Validation des champs
        if not email or not telephone or not date_rendement_str:
            messages.error(request, "Tous les champs sont requis pour emprunter un livre.")
            return redirect("emprunter_livre", livre_id=livre_id)  # Redirection avec l'ID du livre

        try:
            date_rendement = datetime.strptime(date_rendement_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Format de date invalide.")
            return redirect("emprunter_livre", livre_id=livre_id)  # Redirection avec l'ID du livre

        # Vérifier si la date de rendement est dans le futur
        if date_rendement <= date_actuelle:
            messages.error(request, "La date de rendement doit être dans le futur.")
            return redirect("emprunter_livre", livre_id=livre_id)  # Redirection avec l'ID du livre

        # Enregistrer l'emprunt
        Emprunt.objects.create(
            livre=livre,
            utilisateur=request.user,
            email=email,
            telephone=telephone,
            date_emprunt=datetime.now(),
            date_rendement=date_rendement
        )

        # Réduire le nombre d'exemplaires disponibles
        livre.nombre_exemplaires -= 1
        livre.save()

        messages.success(request, f"Vous avez emprunté le livre {livre.titre}.")
        return redirect("les_emprunts")

    return render(request, "bibliotheque/emprunter.html", {"livre": livre, "date_actuelle": date_actuelle})

@login_required
def rendre_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)

    # Utiliser filter pour obtenir les emprunts
    emprunts = Emprunt.objects.filter(livre=livre, utilisateur=request.user)

    # Si plus d'un emprunt est trouvé, on renvoie une erreur
    if emprunts.count() != 1:
        messages.error(request, "Erreur : Il y a un problème avec cet emprunt.")
        return redirect('les_emprunts')

    # Obtenez le premier emprunt trouvé
    emprunt = emprunts.first()

    # Logique pour retourner le livre
    emprunt.date_retour = timezone.now()
    livre.nombre_exemplaires += 1  # Ajouter un exemplaire pour le rendre disponible
    livre.save()

    # Supprimer l'emprunt
    emprunt.delete()

    messages.success(request, f"Le livre {livre.titre} a été rendu avec succès.")
    return redirect('les_emprunts')




@login_required
def signaler_perte(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    emprunt = Emprunt.objects.filter(livre=livre, utilisateur=request.user).first()
    if emprunt:
        # Créer une entrée dans la table des livres perdus
        LivrePerdu.objects.create(
            titre=livre.titre,  # Seul le titre est enregistré dans LivrePerdu
            date_signalement=timezone.now()  # Date actuelle
        )
        # Supprimer l'emprunt
        emprunt.delete()

        # Message de succès
        messages.success(request, "La perte a été signalée avec succès.")
    return redirect('les_emprunts')


@login_required
def les_emprunts_view(request):
    # Récupérer les emprunts de l'utilisateur connecté
    emprunts = Emprunt.objects.filter(utilisateur=request.user)

    # Récupérer tous les livres perdus
    livres_perdus = LivrePerdu.objects.all()

    # Préparer les données pour les livres empruntés
    livres_empruntes = [
        {
            'livre': emprunt.livre,
            'date_emprunt': emprunt.date_emprunt,
            'date_rendement': emprunt.date_rendement,
        }
        for emprunt in emprunts
    ]

    # Retourner les données au template
    return render(request, 'bibliotheque/LesEmprunts.html', {
        'livres_empruntes': livres_empruntes,
        'livres_perdus': livres_perdus,
    })