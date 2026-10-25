# Chill-project (Système de Compilation et Release Cinnabar)

Système de compilation, de synchronisation upstream et de distribution de releases personnalisées pour **Cinnabar** (Minecraft: Bedrock Edition en Rust), conçu sur le modèle de **`xdpdl/cbr-releases`**.

---

## 🎯 Fonctionnalités Principales

1. **Compilation Custom Automatisée** : Compile le client Cinnabar Windows (`.exe` setup et `.msi`) via GitHub Actions sans surcharger votre machine locale.
2. **Synchronisation Upstream Continue** : Récupère les dernières mises à jour de [`cinnabar-mc/cinnabar`](https://github.com/cinnabar-mc/cinnabar) (branche `dev` ou tags officiels) et applique automatiquement vos modifications.
3. **Mise à Jour En Jeu (In-Game Auto-Update)** : Les utilisateurs qui ont installé votre version custom reçoivent et installent directement les mises à jour depuis l'interface du jeu, **sans devoir retélécharger ni réinstaller manuellement le binaire** !
4. **Signature Cryptographique Ed25519** : Les manifests de mise à jour (`update-beta.json`) sont signés cryptographiquement pour être validés par le moteur d'intégrité natif de Cinnabar.
5. **Support Allowlist** : Outil inclus pour générer une liste signée de codes machines autorisés (`allowlist.json`), exactement comme dans `xdpdl/cbr-releases`.

---

## 🏗️ Architecture du Projet

```
cinnabar+++++/
├── comp/           <- Ce repository (regarde-pas/Chill-project)
│   ├── .github/workflows/
│   │   ├── build-and-release.yml   # Workflow principal de compilation & release
│   │   ├── sync-upstream.yml       # Détection auto des updates officielles
│   │   └── generate-keys-action.yml # Générateur de clés de signature (1-clic)
│   ├── scripts/
│   │   ├── keygen.py               # Générateur Ed25519 pur Python
│   │   ├── generate-keys.ps1       # Script PowerShell de clés
│   │   └── sign-allowlist.py       # Générateur d'allowlist signée
│   └── README.md
│
└── code/           <- Votre repository de modifications (regarde-pas/projet-chill)
    ├── patches/    # Fichiers .patch git appliqués sur Cinnabar
    ├── autoclicker/# Modules additionnels personnalisés
    └── scripts/    # Scripts custom
```

---

## 🔄 Comment Fonctionne la Mise à Jour En Jeu ?

1. **Redirection du Repo** : Lors de la compilation, `packaging/release-assets.json` est configuré pour pointer vers `regarde-pas/Chill-project`.
2. **Clé Publique Intégrée** : La variable d'environnement `UPDATE_TRUSTED_KEYS` (ex: `chill1:<CLE_PUBLIQUE>`) est injectée directement dans le binaire Cinnabar.
3. **Publication** : Chaque release génère :
   - `Cinnabar-x64-setup.exe` : Installateur standalone pour les nouveaux joueurs.
   - `update-payload-<sha256>-Cinnabar-x64.msi` : Payload de mise à jour immutable.
   - `update-beta.json` : Manifest signé contenant la version, le SHA256 et l'URL du payload.
4. **Mise à jour en jeu** : Quand un joueur lance le jeu, Cinnabar interroge `https://github.com/regarde-pas/Chill-project/releases/latest/download/update-beta.json`. Il valide la signature Ed25519, détecte la nouvelle version, télécharge le payload MSI et l'installe en direct de manière transparente.

---

## 🚀 Guide de Configuration Rapide

### Étape 1 : Générer les Clés de Signature Ed25519

Vous avez deux options simples :

#### Option A (Directement dans GitHub Actions - Recommandée) :
1. Rendez-vous sur votre repo GitHub **`Chill-project`**.
2. Allez dans l'onglet **Actions** -> Sélectionnez le workflow **`Generate Signing Keys`** -> Cliquez sur **Run workflow**.
3. Dans les logs du job, copiez la clé publique et la clé privée générées.

#### Option B (En local via script) :
Exécutez dans un terminal PowerShell :
```powershell
.\scripts\generate-keys.ps1
```

---

### Étape 2 : Configurer les Secrets et Variables sur GitHub

Dans les paramètres de votre repo GitHub (`https://github.com/regarde-pas/Chill-project/settings`) :

1. **Aller dans `Secrets and variables` -> `Actions`**
2. **Dans l'onglet `Variables`** :
   - Cliquez sur **New repository variable** :
     - **Name** : `UPDATE_TRUSTED_KEYS`
     - **Value** : `chill1:<VOTRE_CLE_PUBLIQUE_BASE64>`
3. **Dans l'onglet `Secrets`** :
   - Cliquez sur **New repository secret** :
     - **Name** : `CINNABAR_UPDATE_SIGNING_KEY`
     - **Value** : `<VOTRE_CLE_PRIVEE_SEED_BASE64>`
   - *(Optionnel si `code` est un repo privé)* Ajoutez un secret `GH_PAT` (Personal Access Token avec permission `repo`) pour permettre au workflow de cloner `regarde-pas/projet-chill`.

---

### Étape 3 : Lancer la Compilation

1. Allez dans l'onglet **Actions** sur GitHub.
2. Choisissez **`Build & Release Custom Cinnabar`**.
3. Cliquez sur **Run workflow** (vous pouvez laisser les options par défaut).
4. GitHub Actions compile automatiquement Cinnabar, applique vos patches, signe le manifest et crée la Release !

---

### Étape 4 : Synchronisation Automatique avec Cinnabar Officiel

Le workflow **`Sync Upstream Cinnabar`** :
- Tourne automatiquement toutes les 6 heures.
- Interroge l'API GitHub de `cinnabar-mc/cinnabar`.
- Dès qu'un nouveau commit officiel est poussé sur la branche `dev`, il déclenche automatiquement une nouvelle compilation et publie la mise à jour pour vos utilisateurs !

---

## 🛡️ Gestion de l'Allowlist (Machines Autorisées)

Pour créer ou mettre à jour une release d'allowlist signée (comme sur `xdpdl/cbr-releases`) :

```powershell
python scripts/sign-allowlist.py <VOTRE_CLE_PRIVEE_SEED_BASE64> "CODE-PC-1" "CODE-PC-2"
```

Le fichier `allowlist.json` généré peut ensuite être attaché à un tag de release `allowlist` sur GitHub.
