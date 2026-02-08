/**
 * ===== SCRIPT PRINCIPAL DE L'APPLICATION =====
 * Gestionnaire de Tâches avec IA - LocalHost Academy
 */

// ===== VARIABLES GLOBALES =====
let currentTheme = localStorage.getItem('theme') || 'light';
let toastContainer = null;

// ===== INITIALISATION =====
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeToasts();
    initializeTheme();
    initializeFormValidation();
    initializeAjaxHandlers();
    initializeKeyboardShortcuts();
    initializeTooltips();
    initializeLazyLoading();
});

// ===== FONCTION D'INITIALISATION PRINCIPALE =====
function initializeApp() {
    console.log('Initialisation de l\'application...');
    
    // Vérifier si Bootstrap est chargé
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap n\'est pas chargé !');
        return;
    }
    
    // Initialiser les composants
    initializeComponents();
    
    console.log('Application initialisée avec succès !');
}

// ===== GESTION DES TOASTS =====
function initializeToasts() {
    // Créer le conteneur de toasts s'il n'existe pas
    if (!document.querySelector('.toast-container')) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    } else {
        toastContainer = document.querySelector('.toast-container');
    }
}

function showToast(message, type = 'info', duration = 5000) {
    const toastId = 'toast-' + Date.now();
    const iconMap = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-triangle',
        'warning': 'fa-exclamation-circle',
        'info': 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas ${iconMap[type]} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });
    
    bsToast.show();
    
    // Supprimer l'élément du DOM après fermeture
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// ===== GESTION DU THÈME =====
function initializeTheme() {
    // Appliquer le thème sauvegardé
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Créer le bouton de changement de thème
    const themeToggle = document.createElement('button');
    themeToggle.className = 'btn btn-outline-light btn-sm position-fixed bottom-0 end-0 m-3';
    themeToggle.style.zIndex = '1000';
    themeToggle.innerHTML = currentTheme === 'dark' ? 
        '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    themeToggle.title = 'Changer le thème';
    
    themeToggle.addEventListener('click', toggleTheme);
    document.body.appendChild(themeToggle);
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    
    // Mettre à jour l'icône
    const themeToggle = document.querySelector('.btn[title="Changer le thème"]');
    themeToggle.innerHTML = currentTheme === 'dark' ? 
        '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        
    showToast(`Thème ${currentTheme === 'dark' ? 'sombre' : 'clair'} activé`, 'info', 2000);
}

// ===== VALIDATION DES FORMULAIRES =====
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focuser sur le premier champ invalide
                const firstInvalid = form.querySelector('.form-control:invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    showToast('Veuillez corriger les erreurs dans le formulaire', 'error');
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Validation en temps réel
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(input);
            });
            
            input.addEventListener('input', function() {
                if (input.classList.contains('is-invalid')) {
                    validateField(input);
                }
            });
        });
    });
}

function validateField(field) {
    const isValid = field.checkValidity();
    
    field.classList.toggle('is-valid', isValid);
    field.classList.toggle('is-invalid', !isValid);
    
    // Gérer les messages d'erreur personnalisés
    let feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!isValid && !feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentNode.appendChild(feedback);
    }
    
    if (feedback) {
        feedback.textContent = isValid ? '' : getCustomErrorMessage(field);
        feedback.style.display = isValid ? 'none' : 'block';
    }
}

function getCustomErrorMessage(field) {
    if (field.validity.valueMissing) {
        return `Le champ "${field.labels[0]?.textContent || field.name}" est obligatoire.`;
    }
    if (field.validity.typeMismatch) {
        return 'Le format saisi n\'est pas valide.';
    }
    if (field.validity.tooShort) {
        return `Minimum ${field.minLength} caractères requis.`;
    }
    if (field.validity.tooLong) {
        return `Maximum ${field.maxLength} caractères autorisés.`;
    }
    return 'Valeur invalide.';
}

// ===== GESTION AJAX =====
function initializeAjaxHandlers() {
    // Configuration globale pour les requêtes AJAX
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const [url, config = {}] = args;
        
        // Ajouter automatiquement le token CSRF
        if (config.method && config.method.toUpperCase() !== 'GET') {
            config.headers = {
                ...config.headers,
                'X-CSRFToken': getCsrfToken()
            };
        }
        
        // Ajouter un indicateur de chargement
        const loadingIndicator = showLoadingIndicator();
        
        return originalFetch(url, config)
            .then(response => {
                hideLoadingIndicator(loadingIndicator);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return response;
            })
            .catch(error => {
                hideLoadingIndicator(loadingIndicator);
                console.error('Erreur AJAX:', error);
                showToast('Erreur de connexion au serveur', 'error');
                throw error;
            });
    };
}

function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }
    
    // Fallback: chercher dans les métadonnées
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    return csrfMeta ? csrfMeta.getAttribute('content') : '';
}

function showLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'loading-indicator position-fixed top-50 start-50 translate-middle';
    indicator.style.zIndex = '9999';
    indicator.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Chargement...</span>
        </div>
    `;
    
    document.body.appendChild(indicator);
    return indicator;
}

function hideLoadingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
    }
}

// ===== RACCOURCIS CLAVIER =====
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + N : Nouvelle tâche
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            const newTaskBtn = document.querySelector('a[href*="task/new"]');
            if (newTaskBtn) {
                newTaskBtn.click();
            }
        }
        
        // Ctrl/Cmd + S : Sauvegarder le formulaire
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            const form = document.querySelector('form');
            if (form) {
                event.preventDefault();
                form.submit();
            }
        }
        
        // Échap : Fermer les modals
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
        
        // Ctrl/Cmd + I : Insights IA
        if ((event.ctrlKey || event.metaKey) && event.key === 'i') {
            event.preventDefault();
            const insightsBtn = document.querySelector('#get-insights-btn');
            if (insightsBtn) {
                insightsBtn.click();
            }
        }
    });
}

// ===== TOOLTIPS ET POPOVERS =====
function initializeTooltips() {
    // Initialiser tous les tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialiser tous les popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// ===== LAZY LOADING =====
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// ===== FONCTIONS UTILITAIRES =====

// Formatage des dates
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return new Intl.DateTimeFormat('fr-FR', {...defaultOptions, ...options}).format(new Date(date));
}

// Débounce pour optimiser les performances
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Copier du texte dans le presse-papiers
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Texte copié dans le presse-papiers', 'success', 2000);
    } catch (err) {
        console.error('Erreur lors de la copie:', err);
        showToast('Erreur lors de la copie', 'error');
    }
}

// Sauvegarde automatique des formulaires
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        const formId = form.id || 'form-' + Date.now();
        
        // Charger les données sauvegardées
        inputs.forEach(input => {
            const savedValue = localStorage.getItem(`autosave-${formId}-${input.name}`);
            if (savedValue && !input.value) {
                input.value = savedValue;
            }
        });
        
        // Sauvegarder automatiquement
        const saveForm = debounce(() => {
            inputs.forEach(input => {
                if (input.value) {
                    localStorage.setItem(`autosave-${formId}-${input.name}`, input.value);
                }
            });
        }, 1000);
        
        inputs.forEach(input => {
            input.addEventListener('input', saveForm);
        });
        
        // Nettoyer après soumission
        form.addEventListener('submit', () => {
            inputs.forEach(input => {
                localStorage.removeItem(`autosave-${formId}-${input.name}`);
            });
        });
    });
}

// ===== GESTION SPÉCIFIQUE AUX TÂCHES =====

// Changer le statut d'une tâche
async function toggleTaskStatus(taskId) {
    try {
        const response = await fetch(`/task/${taskId}/toggle-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Statut changé vers "${data.status_display}"`, 'success');
            
            // Mettre à jour l'interface sans recharger
            updateTaskStatusInDOM(taskId, data.new_status, data.status_display);
        } else {
            throw new Error(data.error || 'Erreur lors du changement de statut');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur lors du changement de statut', 'error');
    }
}

function updateTaskStatusInDOM(taskId, newStatus, statusDisplay) {
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`)?.closest('.task-card');
    if (taskCard) {
        // Mettre à jour le badge de statut
        const statusBadge = taskCard.querySelector('.badge.bg-secondary');
        if (statusBadge) {
            statusBadge.textContent = statusDisplay;
        }
        
        // Ajouter une animation
        taskCard.style.transform = 'scale(1.05)';
        setTimeout(() => {
            taskCard.style.transform = 'scale(1)';
        }, 200);
    }
}

// ===== GESTION DES INSIGHTS IA =====

async function getAIInsights() {
    try {
        const response = await fetch('/api/insights/');
        const data = await response.json();
        
        if (data.success) {
            displayInsights(data.insights);
        } else {
            throw new Error(data.message || data.error);
        }
    } catch (error) {
        console.error('Erreur insights IA:', error);
        showToast('Erreur lors de la génération des insights. Vérifiez qu\'Ollama est démarré.', 'error');
    }
}

function displayInsights(insights) {
    const modal = document.getElementById('insightsModal');
    const contentDiv = document.getElementById('insights-content');
    const loadingDiv = document.getElementById('insights-loading');
    
    if (loadingDiv) loadingDiv.classList.add('d-none');
    
    if (contentDiv) {
        contentDiv.innerHTML = `
            <div class="alert alert-info">
                <strong>Analyse générée le :</strong> ${insights.generated_at}
            </div>
            <div class="insight-text">
                ${insights.analysis.replace(/\n/g, '<br>')}
            </div>
        `;
        contentDiv.classList.remove('d-none');
    }
}

// ===== INITIALISATION DES COMPOSANTS =====
function initializeComponents() {
    // Initialiser les barres de progression
    initializeProgressBars();
    
    // Initialiser les graphiques (si Chart.js est disponible)
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Initialiser la sauvegarde automatique
    initializeAutoSave();
    
    // Initialiser les fonctionnalités de recherche
    initializeSearch();
}

function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar[data-animate]');
    progressBars.forEach(bar => {
        const width = bar.getAttribute('aria-valuenow');
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width + '%';
        }, 500);
    });
}

function initializeSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        const debouncedSearch = debounce((value) => {
            if (value.length >= 2) {
                performSearch(value);
            }
        }, 500);
        
        searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });
    }
}

async function performSearch(query) {
    // Implémenter la recherche en temps réel si nécessaire
    console.log('Recherche:', query);
}

// ===== FONCTIONS D'EXPORT =====

// Exporter pour utilisation globale
window.TaskManager = {
    toggleTaskStatus,
    getAIInsights,
    showToast,
    copyToClipboard,
    formatDate
};

console.log('Script principal chargé avec succès !');
