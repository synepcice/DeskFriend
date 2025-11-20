# DeskFriend

DeskFriend est un assistant de bureau léger et discret conçu pour améliorer votre productivité. Il vous permet de gérer vos tâches, de conserver un historique de votre presse-papier et de garder vos notes importantes toujours à portée de main.


## Fonctionnalités

*   **Listes Multiples** : Créez, renommez et gérez plusieurs listes de tâches ou de notes.
*   **Code Couleur** : Personnalisez la couleur de chaque liste pour une meilleure organisation visuelle.
*   **Gestionnaire de Presse-Papier** :
    *   Enregistre automatiquement l'historique de votre presse-papier.
    *   Détection intelligente des doublons pour éviter l'encombrement.
    *   Possibilité d'activer/désactiver la surveillance du presse-papier.
*   **Recherche Globale** : Retrouvez rapidement n'importe quel élément (texte ou date) à travers toutes vos listes.
*   **Interface Discrète** :
    *   Fenêtre "Toujours au premier plan" (Always on Top) pour garder vos notes visibles.
    *   Transparence et design sombre pour s'intégrer élégamment à votre bureau.
    *   Redimensionnable et déplaçable facilement.
*   **Actions Rapides** :
    *   Menu contextuel pour copier rapidement le contenu des éléments.
    *   Raccourcis et boutons intuitifs.

## Installation

### Prérequis

*   Python 3.10 ou supérieur
*   Les dépendances listées dans `requirements.txt`

### Installation depuis les sources

1.  Clonez le dépôt :
    ```bash
    git clone https://github.com/votre-utilisateur/DeskFriend.git
    cd DeskFriend
    ```

2.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

3.  Lancez l'application :
    ```bash
    python main.py
    ```

## Compilation (Windows)

Pour créer un exécutable autonome `.exe` :

1.  Assurez-vous d'avoir `pyinstaller` installé :
    ```bash
    pip install pyinstaller
    ```

2.  Lancez la compilation via le fichier spec inclus :
    ```bash
    python -m PyInstaller deskfriend.spec
    ```

3.  L'exécutable se trouvera dans le dossier `dist/`.

## Technologies Utilisées

*   **Python** : Langage principal.
*   **PyQt6** : Framework pour l'interface graphique.
*   **JSON** : Stockage des données localement.

## Auteur

Développé avec passion pour simplifier votre flux de travail quotidien.

