# GbGescom - Application de Gestion de Supermarché

## Description
Application web complète de gestion de supermarché développée avec Flask, inspirée de l'interface GbGescom originale.

## Fonctionnalités

### 🏪 Gestion des Produits
- Liste complète avec recherche et filtres avancés
- Ajout, modification, suppression de produits
- Gestion des codes produits, désignations, familles
- Prix multiples (boutique, magasin 1, 2, 3)
- Alertes de stock automatiques

### 📦 Gestion du Stock
- Suivi des niveaux de stock en temps réel
- Alertes pour les produits en rupture
- Mouvements de stock (entrées/sorties/ajustements)
- Système de réapprovisionnement

### 🧾 Facturation
- Création de factures interactives
- Recherche rapide de produits par code ou nom
- Calcul automatique des totaux
- Interface de caisse moderne

### 📊 Rapports et Statistiques
- Tableaux de bord avec graphiques interactifs
- Statistiques par famille de produits
- Analyse de la valeur du stock
- Exports (simulation Excel/PDF)

## Installation et Lancement

### Prérequis
- Python 3.7+
- pip (gestionnaire de paquets Python)

### Installation des dépendances
```bash
pip install Flask==2.3.3 Flask-SQLAlchemy==3.0.5 Flask-WTF==1.1.1 WTForms==3.0.1 Werkzeug==2.3.7 python-dotenv==1.0.0
```

### Lancement de l'application
```bash
python app.py
```

### Accès à l'application
Ouvrir votre navigateur et aller à : **http://localhost:5000**

## Structure du Projet
```
Supermarche/
├── app.py              # Application Flask principale
├── run.py              # Script de lancement
├── requirements.txt    # Dépendances Python
├── README.md          # Ce fichier
├── supermarche.db     # Base de données SQLite (créée automatiquement)
└── templates/         # Templates HTML
    ├── base.html      # Template de base
    ├── index.html     # Page d'accueil
    ├── produits.html  # Liste des produits
    ├── nouveau_produit.html
    ├── modifier_produit.html
    ├── facturation.html
    ├── stock.html
    └── rapports.html
```

## Données d'Exemple
L'application se lance avec des données d'exemple incluant :
- 10 produits de démonstration
- 3 familles de produits (ELECTRICITE, MENAGE, PLOMBERIE)
- Stocks et prix configurés

## Utilisation

### Navigation
- **Accueil** : Tableau de bord principal
- **Produits** : Gestion complète des produits
- **Facturation** : Interface de vente et facturation
- **Stock** : Gestion des stocks et alertes
- **Rapports** : Statistiques et analyses

### Fonctionnalités Clés
1. **Recherche de produits** : Par code ou désignation
2. **Filtres avancés** : Par famille, état du stock
3. **Alertes automatiques** : Produits en rupture de stock
4. **Interface responsive** : Compatible mobile et desktop

## Technologies Utilisées
- **Backend** : Flask (Python)
- **Base de données** : SQLite avec SQLAlchemy
- **Frontend** : Bootstrap 5, Font Awesome
- **Graphiques** : Chart.js

## Développement
Pour contribuer au projet :
1. Cloner le repository
2. Installer les dépendances
3. Lancer en mode développement avec `python app.py`
4. L'application se recharge automatiquement lors des modifications

## Support
Pour toute question ou problème, consultez les logs de l'application ou vérifiez que toutes les dépendances sont correctement installées.

---
**Version** : 1.0  
**Auteur** : Développé avec Cascade AI  
**Licence** : Usage libre pour projets éducatifs et commerciaux

# projetp
