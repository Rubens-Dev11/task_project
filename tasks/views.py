from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
import ollama
import json
import logging
import requests
from .models import Task
from .forms import TaskForm

# Configuration du logging
logger = logging.getLogger(__name__)

class TaskListView(ListView):
    """Vue pour afficher la liste des tâches avec filtres et pagination"""
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10  # 10 tâches par page
    
    def get_queryset(self):
        """Filtre les tâches selon les paramètres de recherche"""
        queryset = Task.objects.all()
        
        # Filtre par statut
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtre par priorité
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Recherche dans le titre et la description
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Ajoute des données supplémentaires au contexte"""
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        context['stats'] = {
            'total': Task.objects.count(),
            'todo': Task.objects.filter(status='todo').count(),
            'doing': Task.objects.filter(status='doing').count(),
            'done': Task.objects.filter(status='done').count(),
            'overdue': sum(1 for task in Task.objects.all() if task.is_overdue()),
        }
        
        # Paramètres de filtre actuels
        context['current_status'] = self.request.GET.get('status', '')
        context['current_priority'] = self.request.GET.get('priority', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context

class TaskDetailView(DetailView):
    """Vue pour afficher le détail d'une tâche"""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

class TaskCreateView(CreateView):
    """Vue pour créer une nouvelle tâche"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def form_valid(self, form):
        """Traitement après validation du formulaire"""
        messages.success(self.request, 'Tâche créée avec succès !')
        return super().form_valid(form)

class TaskUpdateView(UpdateView):
    """Vue pour modifier une tâche existante"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def form_valid(self, form):
        """Traitement après validation du formulaire"""
        messages.success(self.request, 'Tâche modifiée avec succès !')
        return super().form_valid(form)

class TaskDeleteView(DeleteView):
    """Vue pour supprimer une tâche"""
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def delete(self, request, *args, **kwargs):
        """Traitement lors de la suppression"""
        messages.success(self.request, 'Tâche supprimée avec succès !')
        return super().delete(request, *args, **kwargs)

def toggle_task_status(request, pk):
    """Vue AJAX pour changer le statut d'une tâche"""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        
        # Cycle des statuts : todo -> doing -> done -> todo
        status_cycle = {'todo': 'doing', 'doing': 'done', 'done': 'todo'}
        task.status = status_cycle.get(task.status, 'todo')
        task.save()
        
        return JsonResponse({
            'success': True,
            'new_status': task.status,
            'status_display': task.get_status_display()
        })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def check_ollama_connection():
    """Vérifie si Ollama est accessible"""
    try:
        response = requests.get(f"{settings.OLLAMA_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Impossible de se connecter à Ollama : {e}")
        return False

def get_available_models():
    """Récupère la liste des modèles disponibles"""
    try:
        response = requests.get(f"{settings.OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles : {e}")
        return []

def get_ai_insights(request):
    """Vue pour afficher les insights IA"""
    try:
        # Vérification de la connexion Ollama
        if not check_ollama_connection():
            messages.error(request, 'Ollama n\'est pas accessible. Assurez-vous qu\'il est démarré sur le port 11434.')
            return redirect('tasks:task_list')
        
        # Récupération des tâches
        tasks = Task.objects.all()
        
        if not tasks.exists():
            messages.info(request, 'Aucune tâche trouvée. Ajoutez des tâches pour obtenir des insights.')
            return redirect('tasks:task_list')
        
        # Préparation des données pour l'IA
        insights = generate_ai_insights(tasks)
        
        context = {
            'insights': insights,
            'tasks_count': tasks.count(),
        }
        
        return render(request, 'tasks/ai_insights.html', context)
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des insights : {e}")
        messages.error(request, f'Erreur lors de la génération des insights : {str(e)}')
        return redirect('tasks:task_list')

def ai_insights_api(request):
    """API pour les insights IA (appels AJAX)"""
    if request.method == 'GET':
        try:
            # Vérification de la connexion Ollama
            if not check_ollama_connection():
                return JsonResponse({
                    'success': False,
                    'error': 'Ollama n\'est pas accessible'
                })
            
            tasks = Task.objects.all()
            
            if not tasks.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Aucune tâche trouvée'
                })
            
            insights = generate_ai_insights(tasks)
            
            return JsonResponse({
                'success': True,
                'insights': insights
            })
            
        except Exception as e:
            logger.error(f"Erreur API insights : {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def generate_ai_insights(tasks):
    """Génère des insights IA basés sur les tâches"""
    try:
        # Vérifier les modèles disponibles
        available_models = get_available_models()
        logger.info(f"Modèles disponibles : {available_models}")
        
        # Déterminer le modèle à utiliser
        model_to_use = None
        possible_models = [
            settings.OLLAMA_MODEL,  # D'abord le modèle configuré
            'llama3.1:latest',
            'llama3.1',
            'llama3:latest', 
            'llama3',
            'mistral:latest',
            'mistral'
        ]
        
        for model in possible_models:
            if model in available_models:
                model_to_use = model
                break
        
        if not model_to_use:
            if available_models:
                model_to_use = available_models[0]  # Utiliser le premier modèle disponible
                logger.warning(f"Modèle configuré non trouvé, utilisation de {model_to_use}")
            else:
                raise Exception("Aucun modèle Ollama n'est disponible. Veuillez installer un modèle avec 'ollama pull llama3.1'")
        
        # Préparation des données des tâches
        task_data = []
        for task in tasks:
            task_info = {
                'titre': task.title,
                'description': task.description or 'Pas de description',
                'statut': task.get_status_display(),
                'priorité': task.get_priority_display(),
                'créée_le': task.created_at.strftime('%d/%m/%Y'),
                'en_retard': task.is_overdue()
            }
            task_data.append(task_info)
        
        # Statistiques rapides
        stats = {
            'total': len(task_data),
            'à_faire': len([t for t in task_data if t['statut'] == 'À faire']),
            'en_cours': len([t for t in task_data if t['statut'] == 'En cours']),
            'terminées': len([t for t in task_data if t['statut'] == 'Terminé']),
            'en_retard': len([t for t in task_data if t['en_retard']])
        }
        
        # Construction du prompt pour l'IA
        prompt = f"""
        Analyse ces {stats['total']} tâches et fournis des insights utiles en français :

        Statistiques :
        - Total : {stats['total']} tâches
        - À faire : {stats['à_faire']}
        - En cours : {stats['en_cours']}
        - Terminées : {stats['terminées']}
        - En retard : {stats['en_retard']}

        Détail des tâches :
        {json.dumps(task_data, indent=2, ensure_ascii=False)}

        Fournis une analyse structurée avec :
        1. Un résumé général de la situation
        2. Les priorités recommandées
        3. Des conseils d'organisation
        4. Des points d'attention particuliers

        Réponds en français, de manière concise et actionnable.
        """
        
        # Configuration du client Ollama
        client = ollama.Client(host=settings.OLLAMA_URL)
        
        # Appel à Ollama
        logger.info(f"Utilisation du modèle : {model_to_use}")
        response = client.chat(
            model=model_to_use,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            options={
                'temperature': 0.7,
                'top_p': 0.9,
                'num_predict': 800,  # Limiter la longueur de la réponse
            }
        )
        
        insights = response['message']['content']
        
        return {
            'analysis': insights,
            'stats': stats,
            'model_used': model_to_use,
            'generated_at': timezone.now().strftime('%d/%m/%Y à %H:%M')
        }
        
    except Exception as e:
        logger.error(f"Erreur génération insights : {e}")
        error_msg = str(e)
        if "model" in error_msg.lower() and "not found" in error_msg.lower():
            error_msg += "\n\nPour résoudre ce problème :\n1. Ouvrez un terminal\n2. Exécutez : ollama pull llama3.1\n3. Attendez le téléchargement\n4. Réessayez"
        
        return {
            'analysis': f"Erreur lors de la génération des insights : {error_msg}",
            'stats': {},
            'model_used': 'N/A',
            'generated_at': timezone.now().strftime('%d/%m/%Y à %H:%M')
        }