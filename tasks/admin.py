from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour les tâches"""
    
    # Configuration de la liste
    list_display = [
        'title', 
        'status_badge', 
        'priority_badge', 
        'due_date', 
        'created_at',
        'is_overdue_badge',
        'actions_column'
    ]
    
    list_filter = [
        'status',
        'priority', 
        'created_at',
        'due_date'
    ]
    
    search_fields = [
        'title', 
        'description'
    ]
    
    readonly_fields = [
        'created_at', 
        'updated_at',
        'task_details'
    ]
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'description')
        }),
        ('Statut et priorité', {
            'fields': ('status', 'priority', 'due_date')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Détails', {
            'fields': ('task_details',),
            'classes': ('collapse',)
        })
    )
    
    # Configuration de la pagination
    list_per_page = 25
    list_max_show_all = 100
    
    # Actions personnalisées
    actions = [
        'mark_as_todo',
        'mark_as_doing', 
        'mark_as_done',
        'set_high_priority',
        'export_selected_tasks'
    ]
    
    def status_badge(self, obj):
        """Affiche le statut avec un badge coloré"""
        colors = {
            'todo': 'warning',
            'doing': 'info',
            'done': 'success'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def priority_badge(self, obj):
        """Affiche la priorité avec un badge coloré"""
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'dark'
        }
        color = colors.get(obj.priority, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priorité'
    
    def is_overdue_badge(self, obj):
        """Indique si la tâche est en retard"""
        if obj.is_overdue():
            return format_html(
                '<span class="badge bg-danger">En retard</span>'
            )
        return format_html('<span class="badge bg-light">À jour</span>')
    is_overdue_badge.short_description = 'État'
    
    def actions_column(self, obj):
        """Colonne d'actions rapides"""
        view_url = reverse('admin:tasks_task_change', args=[obj.pk])
        return format_html(
            '<a href="{}" class="btn btn-sm btn-outline-primary">Modifier</a>',
            view_url
        )
    actions_column.short_description = 'Actions'
    
    def task_details(self, obj):
        """Affiche les détails de la tâche en HTML"""
        html = f"""
        <div style="font-family: Arial, sans-serif;">
            <h4>Détails de la tâche</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 5px; font-weight: bold;">Titre:</td>
                    <td style="padding: 5px;">{obj.title}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">Description:</td>
                    <td style="padding: 5px;">{obj.description or 'Aucune description'}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">Statut:</td>
                    <td style="padding: 5px;">{obj.get_status_display()}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">Priorité:</td>
                    <td style="padding: 5px;">{obj.get_priority_display()}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">Date d'échéance:</td>
                    <td style="padding: 5px;">{obj.due_date.strftime('%d/%m/%Y à %H:%M') if obj.due_date else 'Aucune'}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">En retard:</td>
                    <td style="padding: 5px;">{'Oui' if obj.is_overdue() else 'Non'}</td>
                </tr>
            </table>
        </div>
        """
        return mark_safe(html)
    task_details.short_description = 'Détails complets'
    
    # Actions personnalisées
    def mark_as_todo(self, request, queryset):
        """Marquer les tâches sélectionnées comme 'À faire'"""
        count = queryset.update(status='todo')
        self.message_user(
            request, 
            f'{count} tâche(s) marquée(s) comme "À faire".'
        )
    mark_as_todo.short_description = 'Marquer comme "À faire"'
    
    def mark_as_doing(self, request, queryset):
        """Marquer les tâches sélectionnées comme 'En cours'"""
        count = queryset.update(status='doing')
        self.message_user(
            request, 
            f'{count} tâche(s) marquée(s) comme "En cours".'
        )
    mark_as_doing.short_description = 'Marquer comme "En cours"'
    
    def mark_as_done(self, request, queryset):
        """Marquer les tâches sélectionnées comme 'Terminé'"""
        count = queryset.update(status='done')
        self.message_user(
            request, 
            f'{count} tâche(s) marquée(s) comme "Terminé".'
        )
    mark_as_done.short_description = 'Marquer comme "Terminé"'
    
    def set_high_priority(self, request, queryset):
        """Définir la priorité comme 'Haute'"""
        count = queryset.update(priority='high')
        self.message_user(
            request, 
            f'{count} tâche(s) définie(s) en priorité haute.'
        )
    set_high_priority.short_description = 'Définir priorité haute'
    
    def export_selected_tasks(self, request, queryset):
        """Exporter les tâches sélectionnées"""
        # Implémentation simplifiée
        tasks_data = []
        for task in queryset:
            tasks_data.append({
                'titre': task.title,
                'description': task.description,
                'statut': task.get_status_display(),
                'priorité': task.get_priority_display(),
                'créée_le': task.created_at.strftime('%d/%m/%Y %H:%M')
            })
        
        # Ici vous pourriez implémenter l'export CSV/Excel
        self.message_user(
            request,
            f'{len(tasks_data)} tâche(s) prête(s) pour export.'
        )
    export_selected_tasks.short_description = 'Exporter les tâches sélectionnées'

# Configuration globale de l'admin
admin.site.site_header = "Administration - Gestionnaire de Tâches IA"
admin.site.site_title = "Admin Tâches IA"
admin.site.index_title = "Tableau de bord administrateur"
