Installation
============

Requirements
------------

* Python 3.4 (no backward compatibility)
* PostgreSQL **only** (no MySQL or SQLite support)

Deployment
----------

Backend
```````

The deployment is the same as any other Django projects. Here is a quick
summary:

1. install required system packages. For example on Debian::

    apt-get install python3 python3-dev postgresql-9.4 libpq-dev virtualenv

2. create a PostgreSQL database in a cluster with role and owner

3. create a virtualenv::

    virtualenv <NAME> -p python3

4. install dependencies with pip (see :ref:`installation-backend-production`
   or :ref:`installation-backend-development`)

5. configure the settings (see :ref:`installation-backend-production` or
   :ref:`installation-backend-development`)

6. export the ``DJANGO_SETTINGS_MODULE`` to easily use the ``manage.py`` with
   the proper production setting. For example::

    export DJANGO_SETTINGS_MODULE="mymoney.settings.production"

7. import the SQL schema::

    ./manage.py migrate

8. create a super user::

    ./manage.py createsuperuser

.. note:: WSGI will use the ``production.py`` settings, whereas ``manage.py``
   will use the ``local.py`` by default.

.. _installation-backend-production:

Production
++++++++++

* Install dependencies (in virtualenv)::

    pip install -r requirements/production.txt

* copy ``mymoney/settings/production.dist`` to
  ``mymoney/settings/production.py`` and edit it::

    cp mymoney/settings/production.dist mymoney/settings/production.py

* install JS libraries **first** with *Bower* (see
  :ref:`installation-deployment-frontend`) then collect statics files::

    ./manage.py collectstatic

* execute the Django check command and apply fixes if needed::

    ./manage.py check --deploy

* Set up cron tasks on server to execute the following commands:

    * cloning recurring bank transactions::

        ./manage.py clonescheduled

    * cleanup tasks (only usefull with further user accounts)::

        ./manage.py deleteorphansbankaccounts

At the project root directory, the ``scripts`` directory provides bash script
wrappers to execute these commands.
Thus, you could create cron rules similar to something like::

    0 1 * * *  ABSOLUTE_PATH/scripts/clonescheduled.sh <ABSOLUTE_PATH_TO_V_ENV>
    0 2 * * *  ABSOLUTE_PATH/scripts/deleteorphansbankaccounts.sh <ABSOLUTE_PATH_TO_V_ENV>

For example, create a file in ``/etc/cron.d/clonescheduled``, and edit::

   0 2 * * * <USER> /ABSOLUTE_PATH/scripts/clonescheduled.sh <ABSOLUTE_PATH_TO_V_ENV>

.. _installation-backend-development:

Development
+++++++++++

* Install dependencies::

    pip install -r requirements/local.txt

* copy ``mymoney/settings/local.dist`` to ``mymoney/settings/local.py`` and
  edit it::

    cp mymoney/settings/local.dist mymoney/settings/local.py

.. _installation-deployment-frontend:

Frontend
````````

1. install `Bower`_. One way is to do it with `npm`_ globally::

    npm install -g bower

2. At the project root directory, run the following command to install JS
   libraries dependencies::

    bower install --production

.. _`Bower`: http://bower.io
.. _`npm`: https://www.npmjs.com

.. _installation-frontend-development:

Development
+++++++++++

1. install *npm* globally to use it as a command line tool::

    npm install -g gulp

2. go to the project root directory and install gulp dependencies::

    npm install

3. once *node* packages are installed *locally* in ``./node_modules``, you
   should be able to execute the following gulp commands implemented in
   ``gulpfile.js``:

   * *js*: concat and minify js
   * *css*: concat and minify css

   To execute all commands at once, from the project root directory, just
   execute::

     gulp

Internationalization
--------------------

1. copy ``mymoney/settings/l10n.dist`` to ``mymoney/settings/l10n.py`` and
   edit it::

     cp mymoney/settings/l10n.dist mymoney/settings/l10n.py

   Further notes about some additional settings:

   * ``USE_L10N_DIST``: Whether to use the minify file including translations.
     It imply that the translated file is generated with *gulp*
     (``mymoney.min.<LANGCODE>.js``). If false (default), additionnal JS
     translations files would be loaded.
   * ``BOOTSTRAP_CALENDAR_LANGCODE``: If ``USE_L10N_DIST`` is false, the
     language code to use to load the translation file at:
     ``mymoney/static/bower_components/bootstrap-calendar/js/language/<LANGCODE>.js``
   * ``BOOTSTRAP_DATEPICKER_LANGCODE``: If ``USE_L10N_DIST`` is false, the
     language code to use to load the translation file at:
     ``mymoney/static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.<LANGCODE>.js``

2. edit your final setting file to use the l10n configuration instead::

    # from .base import *
    from .l10n import *

3. optionally build the minified JS distribution for your language. To achieve
   it, you first need to have *gulp* installed. See section
   :ref:`installation-frontend-development` for more details about *gulp*.
   The ``gulp js`` accept optional parameters:

   * ``--lang``: the IETF language code of the form : *xx-XX*. **Must** be the
     same as the Django ``LANGUAGE_CODE`` setting.
   * ``--lang_bt_cal``: the Bootstrap calendar language code to use. To see the
     list of available code supported, take a look at :
     ``mymoney/static/bower_components/bootstrap-calendar/js/language/<LANGCODE>.js``
   * ``--lang_bt_dp``: the Bootstrap datepicker language code to use. Be
     careful, currently the language code must be of the form *xx* and not
     *xx-XX*. To see the list of available language codes, take a look at :
     ``mymoney/static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.<LANGCODE>.js``

   For example, for a French minify JS file, you should execute::

     gulp js --lang=fr-FR --lang_bt_cal=fr-FR --lang_bt_dp=fr

   .. note:: Seems too much verbose to specify 3 arguments for languages but
       unfortunetly, none of them used the same...

.. note:: Only *French* internationalisation/translations are supported for
   now. But any contributions are welcome!

Demo
----

To have a quick look, you could generate some data with the following
commands::

    ./manage.py demo

You can also clear any data relatives to the project's models with::

    ./manage.py demo --purge

Tests
-----

Whichever method is used, you must create a setting file for testing. Copy
``mymoney/settings/test.dist`` to ``mymoney/settings/test.py`` and edit it::

    cp mymoney/settings/test.dist mymoney/settings/test.py

Tox
```

You can use `Tox`_. At the project root directory without virtualenv, just
execute::

    tox

.. _`Tox`: http://tox.readthedocs.org

Behind the scenes, it runs several *testenv* for:

* `flake8`_
* `isort`_
* `Sphinx`_
* test suites with coverage and report

.. _`flake8`: http://flake8.readthedocs.org
.. _`isort`: https://github.com/timothycrosley/isort
.. _`Sphinx`: http://sphinx-doc.org

Manually
````````

1. install dependencies::

    pip install -r requirements/test.txt

2. then execute tests::

    ./manage.py test --settings=mymoney.settings.test mymoney
