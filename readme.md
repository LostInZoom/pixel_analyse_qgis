## pluging QGIS

**Pixel Energy** est un plugin pour QGIS qui permet d’estimer la consommation énergétique ou de calculer un indicateur  des pixels affichés.

Le plugin est actuellement en développement.

## Prérequis

- Une installation de **QGIS 3.x**.

Le plugin utilise l’environnement Python et les bibliothèques PyQGIS fournis avec QGIS. Aucune installation séparée de Python n’est normalement nécessaire.

## Installation manuelle option 1

Cette version de test peut être installée en copiant le dossier du plugin dans le répertoire des extensions de QGIS.

1. Téléchargez ou récupérez le dossier du plugin contenant notamment `__init__.py`, `metadata.txt` et les fichiers Python du plugin.
2. Ouvrez QGIS.
3. Repérez le répertoire des plugins du profil QGIS. Vous pouvez généralement y accéder depuis **Préférences / Options → Système** ou en ouvrant le dossier du profil utilisateur de QGIS.
4. Dans le répertoire `python/plugins`, copiez le dossier du plugin. Le dossier doit porter le nom attendu par le projet, par exemple `pixel_analyse_qgis`.
5. Vérifiez que `metadata.txt` et `__init__.py` se trouvent directement dans ce dossier, et non dans un sous-dossier supplémentaire.
6. Redémarrez QGIS si le plugin n’apparaît pas.
7. Ouvrez **Extensions → Installer/Gérer les extensions…**, recherchez **Pixel Energy**, puis cochez la case pour l’activer.


## Installation manuelle option 2
1. Téléchargez ou récupérez le dossier du plugin contenant notamment `__init__.py`, `metadata.txt` et les fichiers Python du plugin.
2. zipper le dossier
3. Ouvrez QGIS
4. Ouvrez **Extensions → Installer/Gérer les extensions…**, dans l'onglet "Installer depuis un zip" selectionner le dossier zippé.



## Fonctionnalités

- Analyser une zone rectangulaire sélectionnée sur le canevas de QGIS.
- Analyser l’ensemble du canevas cartographique.
- Calculer des statistiques sur les couleurs des pixels, notamment les composantes rouge, verte et bleue, ainsi que la luminance.
- Choisir un modèle d’écran parmi les modèles intégrés.
- Créer, modifier et supprimer des modèles personnalisés.
- Définir la formule utilisée pour calculer la contribution d’un pixel, avec des constantes configurables.
- Définir, selon le modèle, une formule de sortie pour calculer une puissance estimée ou un indicateur.


## Utilisation

### 1. Ouvrir Pixel Energy

Après avoir activé le plugin, lancez-le depuis son entrée dans le menu ou la barre d’outils de QGIS, selon la configuration de l’interface.

### 2. Choisir un modèle

Sélectionnez le modèle d’écran à utiliser dans la liste proposée. Le résultat dépend notamment de la technologie d’écran, des coefficients et des formules associés au modèle.

Le bouton de gestion des modèles permet de créer, modifier ou supprimer des modèles personnalisés. Les modèles intégrés sont fournis par le plugin et ne sont pas destinés à être modifiés ou supprimés depuis cette interface.

### 3. Analyser une zone ou le canevas

Suivez les boutons et les instructions de la fenêtre du plugin pour :
- sélectionner une zone rectangulaire du canevas à analyser ; ou
- analyser le canevas dans son ensemble.

Consultez le résultat affiché par le plugin. Les statistiques décrivent les pixels de la capture analysée ; elles ne mesurent pas directement la consommation électrique réelle de l’ordinateur ou de l’écran.

### 4. Créer un modèle personnalisé

Dans la fenêtre principale, ouvrez la gestion des modèles puis choisissez l’action de création.

Un modèle personnalisé peut notamment contenir :
- un nom et une technologie d’écran ;
- une formule par pixel ;
- des constantes associées à cette formule, sous la forme d’un tableau **Nom / Valeur** ;
- le type de résultat et, si nécessaire, une formule de sortie ;
- les paramètres complémentaires proposés par l’éditeur.

Pour ajouter une constante à la formule par pixel, utilisez **Ajouter une constante**, puis renseignez son nom et sa valeur numérique. Utilisez ce nom dans la formule. Par exemple, si la formule fait référence à `gamma`, ajoutez une constante nommée `gamma` avec la valeur souhaitée.

Utilisez **Tester les formules** avant d’enregistrer le modèle. Si le test signale une erreur, vérifiez la syntaxe de la formule, les noms des constantes et leurs valeurs.

Les modèles personnalisés sont enregistrés dans les paramètres utilisateur de QGIS. Ils sont donc liés au profil QGIS utilisé et ne sont pas automatiquement partagés avec les autres testeurs.
