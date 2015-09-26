��    A      $      ,      ,     -     J  _   e  �   �  1   u     �  
   �     �  H   �  >     -   K  &   y     �     �     �     �  i   �  0   L  
   }  &   �     �  k   �  >   (     g  Q   m  P   �  P   	     a	  i   e	  �   �	  D   g
  T   �
  	     �     7  �  w     �   �  �   U  �   8  	   %  9   /  %   i  n   �  Q   �  S   P  ]   �  =        @     V  D   l  <   �  w   �  @   f     �  :   �  v   �  <   q  u   �     $  9   ;  �   u  �     $        1  1  F  #   x  !   �  b   �  �   !  2   �               %  P   4  K   �  9   �  1        =     Z     g     |  z   �  :     
   ?  .   J  
   y  {   �  R         S  R   Y  h   �  V        l  l   p  �   �  O   �  V   �  	   2   �   <   >  !  z   O"  �   �"  �   �#  %  �$  	   �%  N   �%  1   &  t   ?&  T   �&  V   	'  b   `'  [   �'     (     =(  j   T(  [   �(  �   )  R   �)     *  O   !*  �   q*  L   �*  |   H+     �+  @   �+  �   #,  1  �,  )   .     +.   *css*: concat and minify css *js*: concat and minify js At the project root directory, run the following command to install JS libraries dependencies:: At the project root directory, the ``scripts`` directory provides bash script wrappers to execute these commands. Thus, you could create cron rules similar to something like:: Behind the scenes, it runs several *testenv* for: Demo Deployment Development For example, create a file in ``/etc/cron.d/clonescheduled``, and edit:: For example, for a French minify JS file, you should execute:: Further notes about some additional settings: Install dependencies (in virtualenv):: Install dependencies:: Installation Internationalization Manually Only *French* internationalisation/translations are supported for now. But any contributions are welcome! PostgreSQL **only** (no MySQL or SQLite support) Production Python 3.4 (no backward compatibility) Requirements Seems too much verbose to specify 3 arguments for languages but unfortunetly, none of them used the same... Set up cron tasks on server to execute the following commands: Tests The deployment is the same as any other Django projects. Here is a quick summary: To execute all commands at once, from the project root directory, just execute:: To have a quick look, you could generate some data with the following commands:: Tox WSGI will use the ``production.py`` settings, whereas ``manage.py`` will use the ``local.py`` by default. Whichever method is used, you must create a setting file for testing. Copy ``mymoney/settings/test.dist`` to ``mymoney/settings/test.py`` and edit it:: You can also clear any data relatives to the project's models with:: You can use `Tox`_. At the project root directory without virtualenv, just execute:: `Sphinx`_ ``--lang_bt_cal``: the Bootstrap calendar language code to use. To see the list of available code supported, take a look at : ``mymoney/static/bower_components/bootstrap-calendar/js/language/<LANGCODE>.js`` ``--lang_bt_dp``: the Bootstrap datepicker language code to use. Be careful, currently the language code must be of the form *xx* and not *xx-XX*. To see the list of available language codes, take a look at : ``mymoney/static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.<LANGCODE>.js`` ``--lang``: the IETF language code of the form : *xx-XX*. **Must** be the same as the Django ``LANGUAGE_CODE`` setting. ``BOOTSTRAP_CALENDAR_LANGCODE``: If ``USE_L10N_DIST`` is false, the language code to use to load the translation file at: ``mymoney/static/bower_components/bootstrap-calendar/js/language/<LANGCODE>.js`` ``BOOTSTRAP_DATEPICKER_LANGCODE``: If ``USE_L10N_DIST`` is false, the language code to use to load the translation file at: ``mymoney/static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.<LANGCODE>.js`` ``USE_L10N_DIST``: Whether to use the minify file including translations. It imply that the translated file is generated with *gulp* (``mymoney.min.<LANGCODE>.js``). If false (default), additionnal JS translations files would be loaded. `flake8`_ cleanup tasks (only usefull with further user accounts):: cloning recurring bank transactions:: configure the settings (see :ref:`installation-backend-production` or :ref:`installation-backend-development`) copy ``mymoney/settings/l10n.dist`` to ``mymoney/settings/l10n.py`` and edit it:: copy ``mymoney/settings/local.dist`` to ``mymoney/settings/local.py`` and edit it:: copy ``mymoney/settings/production.dist`` to ``mymoney/settings/production.py`` and edit it:: create a PostgreSQL database in a cluster with role and owner create a super user:: create a virtualenv:: edit your final setting file to use the l10n configuration instead:: execute the Django check command and apply fixes if needed:: export the ``DJANGO_SETTINGS_MODULE`` to easily use the ``manage.py`` with the proper production setting. For example:: go to the project root directory and install gulp dependencies:: import the SQL schema:: install *gulp* globally to use it as a command line tool:: install JS libraries **first** with *Bower* (see :ref:`installation-deployment-frontend`) then collect statics files:: install `Bower`_. One way is to do it with `npm`_ globally:: install dependencies with pip (see :ref:`installation-backend-production` or :ref:`installation-backend-development`) install dependencies:: install required system packages. For example on Debian:: once *node* packages are installed *locally* in ``./node_modules``, you should be able to execute the following gulp commands implemented in ``gulpfile.js``: optionally build the minified JS distribution for your language. To achieve it, you first need to have *gulp* installed. See section :ref:`installation-frontend-development` for more details about *gulp*. The ``gulp js`` accept optional parameters: test suites with coverage and report then execute tests:: Project-Id-Version: MyMoney 1.0
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2015-07-28 21:33+0200
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
 *css*: concatène et minifie la css *js*: concatène et minifie le js À la racine du projet, exécutez la commande suivante pour installer les librairies JS requises:: À la racine du projet, le répertoire ``scripts`` fourni des scripts bash pour exécuter ces commandes. Par conséquent, vous pouvez les utiliser en créant des règles cron similaire à:: En coulisses, plusieurs *testenv* sont exécutés: Démo Déploiement Développement Par exemple, créez un fichier à ``/etc/cron.d/clonescheduled``, puis éditez:: Par exemple pour un fichier JS minifié français, vous devriez exécuter:: Plusieurs remarques sur les paramètres supplémentaires: Installer les dépendances (dans un virtualenv):: Installer les dépendances:: Installation Internationalisation Manuellement Les traductions en *français* sont uniquement supportées pour le moment. Mais toutes contributions sont les bienvenues ! PostgreSQL **uniquement** (pas de support MySQL ou SQLite) Production Python 3.4 (pas de compabitilité descendante) Prérequis Il semble trop verbeux d'avoir 3 arguments pour la langue mais malheureusement, aucun d'entre eux n'utilisent les mêmes... Configurer des tâches cron sur le serveur pour exécuter les commandes suivantes: Tests Le déploiement est similaire à d'autres projets Django. Voici un bref résumé : Pour exécuter toutes les commandes d'un coup, à partir de la racine du projet, il suffit d'éxecuter:: Pour un aperçu rapide, vous pouvez générer des données avec la commande suivante:: Tox WSGI utilisera les paramètres ``production.py`` alors que ``manage.py`` utilisera ``local.py`` par défaut. Qu'importe la méthode utilisée, vous devez créer un fichier de configuration de test. Copiez ``mymoney/settings/test.dist`` à ``mymoney/settings/test.py`` et éditez le. Vous pouvez aussi nettoyer les données relatives aux modèles du projet avec:: Vous pouvez utiliser `Tox`_. À la racine du projet sans virtualenv, exécutez juste:: `Sphinx`_ ``--lang_bt_cal``: La langue de Bootstrap calendar à utiliser. Pour connaître la liste des codes disponibles, jetez un oeil à : ``mymoney/static/bower_components/bootstrap-calendar/js/language/<LANGCODE>.js`` ``--lang_bt_dp``: le code langue de Bootstrap datepicker à utiliser. Attention actuellement, le code langue est de la forme *xx* et non *xx-XX*. Pour connaître la liste des codes langues disponibles, regardez à : ``mymoney/static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.<LANGCODE>.js`` ``--lang``: le code langue IETF de la forme : *xx-XX*. **Doit** être le même que le paramètre Django ``LANGUAGE_CODE``. ``BOOTSTRAP_CALENDAR_LANGCODE``: Si ``USE_L10N_DIST`` est faux, le code langue à utiliser pour charger le fichier de traduction à: ``mymoney/static/bower_components/bootstrap-calendar/js/language/<LANGCODE>.js`` ``BOOTSTRAP_DATEPICKER_LANGCODE``: Si ``USE_L10N_DIST`` est faux, le code langue à utiliser pour charger le fichier de traduction à: ``mymoney/static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.<LANGCODE>.js`` ``USE_L10N_DIST``: Faut-il ou non utiliser le fichier minifié qui inclut les traductions. Cela implique que le fichier minifié avec traductions a été généré avec *gulp* (``mymoney.min.<LANGCODE>.js``). Si c'est faux (par défaut), les fichiers JS de traductions seront chargés en plus. `flake8`_ tâches de nettoyages (utile uniquement avec plusieurs comptes utilisateurs):: dupliquer les transactions bancaires récurrentes configurer les paramètres ( voir :ref:`installation-backend-production` ou :ref:`installation-backend-development`) copiez ``mymoney/settings/l10n.dist`` à ``mymoney/settings/l10n.py`` et éditez le. copiez ``mymoney/settings/local.dist`` à ``mymoney/settings/local.py`` et éditez le. copier ``mymoney/settings/production.dist`` en ``mymoney/settings/production.py`` puis l'éditer:: créer un cluster de base de données pour PostgreSQL ainsi qu'un rôle et un propriétaire créer un super utilisateur:: créer un virtualenv:: éditez votre fichier de configuration finale pour utiliser le fichier de configuration l10n à la place:: exécuter la commande de vérification de Django puis appliquer des corrections si besoin:: exporter la variable d'environnement ``DJANGO_SETTINGS_MODULE`` pour facilement utiliser ``manage.py`` avec les paramètres de production. Par exemple:: aller dans le répertoire racine du projet et installer les dépendances de gulp:: importer le schéma SQL:: installer globalement *gulp* pour l'utiliser comme outil de ligne de commande:: installer les librairies JS **avant** avec *Bower* (voir :ref:`installation-deployment-frontend`) puis collecter les fichiers statiques:: installer `Bower`_. Une des façon de le faire est avec `npm`_ globalement:: installer les dépendances avec pip (voir :ref:`installation-backend-production` ou :ref:`installation-backend-development`) installer les dépendances:: installer les paquets systèmes requis. Par exemple sur Debian:: une fois les paquets *node* installés *en local* dans ``./node_modules``, vous devriez pouvoir exécuter les commandes gulp suivantes implémentées dans ``gulpfile.js``: optionnellement, construisez le fichier JS minifié de la distribution pour votre langue. Pour y parvenir, vous devez d'abord avoir *gulp* d'installé. Voir la section :ref:`installation-frontend-development` pour plus de détails à propos de *gulp*. La commande ``gulp js`` a des paramètres optionnels: suite de tests avec couverture et rapport puis exécutez les tests:: 