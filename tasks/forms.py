from django import forms
from django.utils import timezone
from .models import Task

class TaskForm(forms.ModelForm):
    """Formulaire pour créer et modifier les tâches"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la tâche',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée (optionnelle)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
        
        labels = {
            'title': 'Titre de la tâche',
            'description': 'Description',
            'status': 'Statut',
            'priority': 'Priorité',
            'due_date': 'Date d\'échéance'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Rendre certains champs obligatoires
        self.fields['title'].required = True
        
        # Personnaliser l'aide contextuelle
        self.fields['due_date'].help_text = 'Format : JJ/MM/AAAA HH:MM'
    
    def clean_due_date(self):
        """Validation de la date d'échéance"""
        due_date = self.cleaned_data.get('due_date')
        
        if due_date and due_date < timezone.now():
            raise forms.ValidationError('La date d\'échéance ne peut pas être dans le passé.')
        
        return due_date
    
    def clean_title(self):
        """Validation du titre"""
        title = self.cleaned_data.get('title')
        
        if title and len(title.strip()) < 3:
            raise forms.ValidationError('Le titre doit contenir au moins 3 caractères.')
        
        return title.strip() if title else title

class TaskFilterForm(forms.Form):
    """Formulaire pour filtrer les tâches"""
    
    STATUS_CHOICES = [('', 'Tous les statuts')] + Task.STATUS_CHOICES
    PRIORITY_CHOICES = [('', 'Toutes les priorités')] + Task.PRIORITY_CHOICES
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher dans les tâches...'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )