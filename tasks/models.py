from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Task(models.Model):
    """
    Modèle représentant une tâche dans notre application.
    """
    
    # Choix pour le statut de la tâche
    STATUS_CHOICES = [
        ('todo', 'À faire'),
        ('doing', 'En cours'),
        ('done', 'Terminé'),
    ]
    
    # Choix pour la priorité
    PRIORITY_CHOICES = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('urgent', 'Urgente'),
    ]
    
    # Champs de la tâche
    title = models.CharField(
        max_length=200,
        verbose_name="Titre de la tâche",
        help_text="Décrivez brièvement votre tâche"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description détaillée",
        help_text="Ajoutez plus de détails si nécessaire"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name="Statut"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Priorité"
    )
    
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Date d'échéance"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    # Optionnel : associer les tâches à un utilisateur
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
        ordering = ['-created_at']  # Tri par date de création décroissante
    
    def __str__(self):
        """Représentation textuelle de la tâche"""
        return f"{self.title} ({self.get_status_display()})"
    
    def is_overdue(self):
        """Vérifie si la tâche est en retard"""
        if self.due_date and self.status != 'done':
            return timezone.now() > self.due_date
        return False
    
    def get_priority_class(self):
        """Retourne une classe CSS basée sur la priorité"""
        priority_classes = {
            'low': 'priority-low',
            'medium': 'priority-medium',
            'high': 'priority-high',
            'urgent': 'priority-urgent'
        }
        return priority_classes.get(self.priority, 'priority-medium')
