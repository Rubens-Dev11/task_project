from django.urls import path
from . import views

# Namespace pour éviter les conflits d'URLs
app_name = 'tasks'

urlpatterns = [
    # Page d'accueil - liste des tâches
    path('', views.TaskListView.as_view(), name='task_list'),
    
    # Détail d'une tâche
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    
    # Créer une nouvelle tâche
    path('task/new/', views.TaskCreateView.as_view(), name='task_create'),
    
    # Modifier une tâche
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    
    # Supprimer une tâche
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    
    # Changer le statut d'une tâche (AJAX)
    path('task/<int:pk>/toggle-status/', views.toggle_task_status, name='task_toggle_status'),
    
    # Obtenir des insights IA
    path('insights/', views.get_ai_insights, name='ai_insights'),
    
    # API pour les insights (pour les appels AJAX)
    path('api/insights/', views.ai_insights_api, name='ai_insights_api'),
]
