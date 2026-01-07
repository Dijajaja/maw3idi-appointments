# Diagrammes UML - Système de Gestion de Rendez-vous

Ce dossier contient les diagrammes UML du système de gestion de rendez-vous Django, générés au format PlantUML.

## Diagrammes Disponibles

### 1. Diagramme de Classe (`diagramme_classe.puml`)
Représente la structure des modèles Django et leurs relations :
- **Modèles principaux** : Service, StaffMember, AppointmentRequest, Appointment
- **Modèles de configuration** : Config, PaymentInfo
- **Modèles auxiliaires** : DayOff, WorkingHours, EmailVerificationCode, PasswordResetToken
- **Relations** : OneToOne, ForeignKey, ManyToMany entre les différentes entités

### 2. Diagramme de Séquence - Réservation (`diagramme_sequence_reservation.puml`)
Illustre le processus complet de réservation d'un rendez-vous :
- Sélection du service
- Soumission de la demande
- Saisie des informations client
- Création du rendez-vous
- Gestion du paiement
- Confirmation

### 3. Diagramme de Séquence - Paiement (`diagramme_sequence_paiement.puml`)
Détaille le processus de paiement avec les différentes méthodes :
- Paiement par carte bancaire
- Virement bancaire
- Portefeuilles électroniques (Bankily, Masrvi, Click, Sedad, Amanty)

### 4. Diagramme de Séquence - Reprogrammation (`diagramme_sequence_reprogrammation.puml`)
Illustre le processus de reprogrammation d'un rendez-vous :
- Vérification des autorisations et limites
- Sélection de la nouvelle date/heure
- Création de l'historique de reprogrammation
- Confirmation et notification

### 5. Diagramme de Cas d'Utilisation (`diagramme_cas_utilisation.puml`)
Présente les fonctionnalités du système organisées par acteur :
- **Client** : Consultation, réservation, gestion des rendez-vous
- **Membre du Personnel** : Gestion des rendez-vous, horaires, services
- **Administrateur** : Gestion complète du système

### 6. Diagramme de Composants (`diagramme_composants.puml`)
Montre l'architecture technique du système :
- Couche Présentation (Vues, Templates, Formulaires)
- Couche Logique Métier (Services, Utils)
- Couche Données (Modèles, Base de données)
- Couche Infrastructure (Configuration, URLs, Email, Logger)

## Images PNG Disponibles ✅

**Les images PNG ont déjà été générées et sont disponibles dans ce dossier !**

Vous trouverez les fichiers suivants :
- `diagramme_classe.png` - Diagramme de classe complet
- `diagramme_sequence_reservation.png` - Processus de réservation
- `diagramme_sequence_paiement.png` - Processus de paiement
- `diagramme_sequence_reprogrammation.png` - Processus de reprogrammation
- `diagramme_cas_utilisation.png` - Cas d'utilisation
- `diagramme_composants.png` - Architecture des composants

## Régénération des Images

Si vous modifiez les fichiers `.puml` et souhaitez régénérer les images :

### Option 1 : Script Python (Recommandé)
```bash
python generate_images.py
```

### Option 2 : Script Batch Windows
Double-cliquer sur `generer_images.bat`

### Option 3 : Utiliser un Éditeur en Ligne
1. Aller sur [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
2. Copier le contenu d'un fichier `.puml`
3. Coller dans l'éditeur
4. Le diagramme sera généré automatiquement
5. Télécharger l'image générée

### Option 4 : Utiliser VS Code
1. Installer l'extension "PlantUML" dans VS Code
2. Ouvrir un fichier `.puml`
3. Utiliser `Alt+D` pour prévisualiser
4. Exporter l'image depuis la prévisualisation

### Option 5 : Utiliser un Outil Local
1. Installer Java
2. Télécharger PlantUML JAR depuis [plantuml.com](https://plantuml.com/download)
3. Générer les images avec :
```bash
java -jar plantuml.jar diagramme_classe.puml
```

## Notes Importantes

- **Diagramme d'activité exclu** : Comme demandé, le diagramme d'activité n'est pas inclus dans cette documentation.
- **Format PlantUML** : Tous les diagrammes sont au format PlantUML, qui est un standard ouvert et facilement modifiable.
- **Mise à jour** : Ces diagrammes doivent être mis à jour si la structure du système change.

## Structure des Fichiers

```
docs/uml/
├── README.md                              # Ce fichier
├── diagramme_classe.puml                  # Diagramme de classe
├── diagramme_sequence_reservation.puml    # Séquence - Réservation
├── diagramme_sequence_paiement.puml       # Séquence - Paiement
├── diagramme_sequence_reprogrammation.puml # Séquence - Reprogrammation
├── diagramme_cas_utilisation.puml         # Cas d'utilisation
└── diagramme_composants.puml              # Architecture composants
```

## Liens Utiles

- [Documentation PlantUML](https://plantuml.com/)
- [Guide des diagrammes UML](https://plantuml.com/guide)
- [Documentation des modèles](../models.md)

