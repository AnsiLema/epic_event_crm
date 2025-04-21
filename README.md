# 📊 Epic Events CRM

Epic Events CRM est une application en ligne de commande (CLI) conçue pour permettre à l'entreprise Epic Events de gérer ses clients, contrats, événements et collaborateurs, tout en respectant les règles de sécurité et les rôles de chaque utilisateur.

##  Fonctionnalités principales

-  Authentification sécurisée avec JWT
-  Gestion des collaborateurs avec rôles (`gestion`, `commercial`, `support`)
-  Création et suivi des contrats
-  Suivi et gestion des événements liés aux contrats
-  Gestion des clients par les commerciaux
-  Permissions strictes selon les rôles (RBAC)
-  Interface en ligne de commande (CLI) avec Click
-  Journalisation des actions sensibles avec Sentry

## 🗂 Architecture

Le projet est organisé selon l'architecture suivante :

epic_event_CRM
    cli/
├── cli/                  # Commandes CLI (Click)
│   ├── auth_commands.py
│   ├── client_commands.py
│   ├── contract_commands.py

│   ├── event_commands.py

│   └── collaborator_commands.py

│
├── bl/                   # Business Logic Layer (règles métier)
├── dal/                  # Data Access Layer (accès base de données)
├── dtos/                 # Data Transfer Objects
├── models/               # Modèles SQLAlchemy
├── security/             # Auth, JWT, permissions, mots de passe
├── db/                   # Session, init de la DB, données de départ
├── monitoring/           # Intégration Sentry
├── tests/                # Tests unitaires
├── .env                  # Variables d’environnement (non suivi par git)
├── requirements.txt      # Dépendances du projet
└── main.py               # Point d’entrée CLI


## 👤 Rôles & permissions

| Rôle       | Accès                                                                                                                                     |
|------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Gestion    | 🔧 Gérer tous les collaborateurs, contrats, et assigner des supports aux événements                                                      |
| Commercial | 📞 Gérer ses clients, créer événements liés à ses contrats signés, filtrer les contrats                                                  |
| Support    | 🛠️ Voir et modifier les événements qui lui sont attribués                                                                                 |

## ⚙️ Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-utilisateur/epic-event-crm.git
cd epic-event-crm
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Créer le fichier .env

Il contiendra la clé secrète pour la génération de tokens. Ainsi que la clé pour sentry, l'outil de journalisation.

```bash
SECRET_KEY="Votre clé secrète JWT"

SENTRY_DSN="Entrez votre DSN depuis votre projet créé dans Sentry"
```
⚠️ Ne jamais versionner .env (ajoutez le au fichier .gitignore)


### 5. Initialiser la base de données + roles + admin (afin de créer les collaborateurs)

```bash
python main.py init all
```


## 🖥️ Utilisation CLI

### Connexion
```bash
python main.py auth login
```

### Créer un collaborateur
```bash
python main.py collaborateur create
```

### Voir les contrats
```bash
python main.py contract list
```

### Autres exemples de commandes :
```bash
python main.py contract signed
python main.py client list
python main.py event list
python main.py collaborator update
```

## Journalisation avec Sentry

Les actions suivantes sont journalisées :
- Erreurs inattendues
- Création et modification de collaborateurs
- Signature d'un contrat
