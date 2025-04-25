# 📊 Epic Events CRM

Epic Events CRM est une application en ligne de commande (CLI) conçue pour permettre à l'entreprise Epic Events de 
gérer ses clients, contrats, événements et collaborateurs, tout en respectant les règles de sécurité et les rôles 
de chaque utilisateur.

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

## 🗂️ Architecture du projet

```text
epic_event_crm/
├── bl/                  # Business Logic Layer
│   ├── client_bl.py
│   ├── collaborator_bl.py
│   ├── contract_bl.py
│   ├── event_bl.py
│   ├── role_bl.py
├── cli/                 # Interface CLI (Click)
│   ├── auth_commands.py
│   ├── auth_decorator.py
│   ├── collaborator_commands.py
│   ├── client_commands.py
│   ├── contract_commands.py
│   └── event_commands.py
├── dal/                 # Data Access Layer
│   ├── client_dal.py
│   ├── collaborator_dal.py
│   ├── contract_dal.py
│   ├── event_dal.py
│   ├── role_dal.py
├── db/                  # Session DB, initialisation, données initiales
│   ├── database_init.py
│   ├── session.py
├── dtos/                # Data Transfer Objects
│   ├── client_dto.py
│   ├── collaborator_dto.py
│   ├── contract_dto.py
│   ├── event_dto.py
│   ├── role_dto.py
├── models/              # Modèles SQLAlchemy
│   ├── base.py
│   ├── client.py
│   ├── collaborator.py
│   ├── contract.py
│   ├── event.py
│   ├── role.py
├── monitoring/          # Intégration Sentry
├── security/            # Auth, JWT, permissions, hashing
├── tests/               # Tests unitaires
├── .env                 # Variables d’environnement (⚠️ non suivi par git)
├── main.py              # Point d’entrée principal
└── requirements.txt     # Dépendances Python
```

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
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
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

## Gestion des collaborateurs


| Commande                                | Rôle requis | Description                    |
|-----------------------------------------|-------------|--------------------------------|
| python main.py collaborator create      | gestion     | Créer un nouveau collaborateur |
| python main.py collaborator list        | Tous        | Lister tous les collaborateurs |
| python main.py collaborator update <id> | gestion   | Mettre à jour un collaborateur |
| python main.py collaborator delete <id> | gestion   | Supprimer un collaborateur     |

## Gestion des clients


| Commande                                | Rôle requis | Description                |
|-----------------------------------------|-------------|----------------------------|
| python main.py client create            | commercial  | Créer un nouveau client    |
| python main.py client list              | Tous        | Lister tous les clients    |
| python main.py client update <id>       | commercial  | Mettre à jour un client    |


## Gestion des contrats


| Commande                            | Rôle requis                             | Description                       |
|-------------------------------------|-----------------------------------------|-----------------------------------|
| python main.py contract create      | gestion                                 | Créer un nouveau contrat          |
| python main.py contract list        | Tous                                    | Lister tous les contrats          |
| python main.py contract update <id> | gestion / commercial (sur ses contrats) | Mettre à jour un client           |
| python main.py contract show <id>   | Tous                                    | Afficher les détails d'un contrat |
| python main.py contract signed      | commercial (sur ses contrats)           | Lister les contrats signés        |
| python main.py contract unsigned    | commercial  (sur ses contrats)          | Lister les contrats non-signés    |
| python main.py contract unsigned    | commercial  (sur ses contrats)          | Lister les contrats non-payés     |


## Gestion des évènements


| Commande                      | Rôle requis                  | Description                                |
|-------------------------------|------------------------------|--------------------------------------------|
| python main.py event create   | commercial                   | Créer un nouveau évènement (contrat signé) |
| python main.py event list     | Tous                         | Lister tous les évènement                  |
| python main.py event update <id> | support / gestion            | Mettre à jour un évènement selon le rôle   |
| python main.py event nosupport | gestion                      | Lister les évènements sans support         |
| python main.py event myevents | support (sur ses évènements) | Lister les évènements assignés au support  |



## Journalisation avec Sentry

Les actions suivantes sont journalisées :
- Exceptions inattendues
- Création et modification de collaborateurs
- Signature d'un contrat


## Auteur
Créé par A'nsi (ansilema@gmail.com)
