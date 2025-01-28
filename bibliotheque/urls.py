from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import rechercher_livre

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('accueil/', views.accueil_view, name='accueil'),
    path('', views.login_view, name='home'),  # Redirige vers la page de connexion par défaut
    path('les-emprunts/', views.les_emprunts_view, name='les_emprunts'),
    path('add-livre/', views.add_livre, name='add_livre'),
    path('livres/', views.list_livres, name='list_livres'),
    path('emprunter/<int:livre_id>/', views.emprunter_livre, name='emprunter_livre'),
    path('rendre/<int:livre_id>/', views.rendre_livre, name='rendre_livre'),
    path('perdre/<int:livre_id>/', views.signaler_perte, name='perdre_livre'),
    path('rechercher-livre/', rechercher_livre, name='rechercher_livre'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
