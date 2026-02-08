#!/usr/bin/env python3
"""
Script de configuration et vérification d'Ollama pour l'application Django
"""

import requests
import subprocess
import sys
import time
from pathlib import Path

def check_ollama_running():
    """Vérifie si Ollama est en cours d'exécution"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_models():
    """Récupère les modèles disponibles"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except:
        return []

def pull_model(model_name):
    """Télécharge un modèle Ollama"""
    print(f"Téléchargement du modèle {model_name}...")
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ Modèle {model_name} téléchargé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du téléchargement : {e}")
        return False
    except FileNotFoundError:
        print("❌ Ollama n'est pas installé ou n'est pas dans le PATH")
        return False

def create_directories():
    """Crée les dossiers nécessaires"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("✅ Dossier logs créé")

def main():
    print("🔧 Configuration d'Ollama pour l'application Django")
    print("=" * 50)
    
    # Créer les dossiers nécessaires
    create_directories()
    
    # Vérifier si Ollama est en cours d'exécution
    print("1. Vérification du service Ollama...")
    if not check_ollama_running():
        print("❌ Ollama n'est pas en cours d'exécution")
        print("   Démarrez Ollama avec : ollama serve")
        print("   Ou installez Ollama depuis : https://ollama.ai")
        return False
    
    print("✅ Ollama est en cours d'exécution")
    
    # Vérifier les modèles disponibles
    print("\n2. Vérification des modèles disponibles...")
    models = get_available_models()
    
    if models:
        print(f"✅ Modèles disponibles : {', '.join(models)}")
        
        # Vérifier si llama3.1 est disponible
        preferred_models = ['llama3.1:latest', 'llama3.1', 'llama3:latest', 'llama3']
        has_preferred = any(model in models for model in preferred_models)
        
        if not has_preferred:
            print("⚠️  Aucun modèle LLaMA détecté")
            response = input("Voulez-vous télécharger llama3.1? (o/N): ")
            if response.lower() in ['o', 'oui', 'y', 'yes']:
                if pull_model("llama3.1"):
                    print("✅ Modèle llama3.1 installé")
                else:
                    print("❌ Échec de l'installation du modèle")
                    return False
        else:
            print("✅ Modèle LLaMA disponible")
    else:
        print("❌ Aucun modèle disponible")
        response = input("Voulez-vous télécharger llama3.1? (o/N): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            if pull_model("llama3.1"):
                print("✅ Modèle llama3.1 installé")
            else:
                print("❌ Échec de l'installation du modèle")
                return False
    
    # Test de connexion
    print("\n3. Test de l'API Ollama...")
    try:
        import ollama
        client = ollama.Client(host='http://localhost:11434')
        
        # Test avec le premier modèle disponible
        final_models = get_available_models()
        if final_models:
            test_model = final_models[0]
            print(f"Test avec le modèle : {test_model}")
            
            response = client.chat(
                model=test_model,
                messages=[{'role': 'user', 'content': 'Dis juste "OK" en français'}],
                options={'num_predict': 10}
            )
            
            print(f"✅ Réponse du modèle : {response['message']['content']}")
            print("✅ Configuration terminée avec succès!")
            return True
        else:
            print("❌ Aucun modèle disponible pour le test")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Votre application est prête à utiliser l'IA!")
        print("Vous pouvez maintenant lancer : python manage.py runserver")
    else:
        print("\n💥 Configuration échouée. Consultez les messages d'erreur ci-dessus.")
        sys.exit(1)