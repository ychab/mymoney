Installation
============

Requirements
------------

* Python 3.4 (no backward compatibility)
* PostgreSQL **only** (no MySQL or SQLite support)

Deployment
----------

The deployment is the same as any other Django projects. Here is a quick
summary:

1. install required system packages. For example on Debian::

    apt-get install python3 python3-dev postgresql-9.4 libpq-dev virtualenv

2. create a PostgreSQL database in a cluster with role and owner

3. create a virtualenv::

    virtualenv <NAME> -p python3

4. install dependencies with pip (see :ref:`installation-deployment-production`
   or :ref:`installation-deployment-development`)

5. configure the settings (see :ref:`installation-deployment-production` or
   :ref:`installation-deployment-development`)

6. export the ``DJANGO_SETTINGS_MODULE`` to easily use the ``manage.py`` with
   the proper production setting. For example::

    export DJANGO_SETTINGS_MODULE="mymoney.settings.production"

7. import the SQL schema::

    ./manage.py migrate

8. create a super user::

    ./manage.py createsuperuser

.. note:: WSGI will use the ``production.py`` settings, whereas ``manage.py``
   will use the ``local.py`` by default.

.. _installation-deployment-production:

Production
``````````

* Install dependencies (in virtualenv)::

    pip install -r requirements/production.txt

* copy ``mymoney/settings/production.dist`` to
  ``mymoney/settings/production.py`` and edit it.

* collect statics files::

    ./manage.py collectstatic

* execute the Django check command and apply fixes if needed::

    ./manage.py check --deploy

* Set up cron tasks on server to execute the following commands:

    * cloning recurring bank transactions::

        ./manage.py clonescheduled

    * cleanup tasks (only usefull with further user accounts)::

        ./manage.py deleteorphansbankaccounts

At the project root directory, the ``scripts`` directory provide bash scripts
wrappers to execute these commands.
Thus, you could create cron rules similar to something like::

    0 1 * * *  ABSOLUTE_PATH/scripts/clonescheduled.sh <ABSOLUTE_PATH_TO_V_ENV>
    0 2 * * *  ABSOLUTE_PATH/scripts/deleteorphansbankaccounts.sh <ABSOLUTE_PATH_TO_V_ENV>

For example, create a file in ``/etc/cron.d/clonescheduled``, and edit::

   0 2 * * * <USER> /ABSOLUTE_PATH/scripts/clonescheduled.sh <ABSOLUTE_PATH_TO_V_ENV>

.. _installation-deployment-development:

Development
```````````

* Install dependencies::

    pip install -r requirements/local.txt

* copy ``mymoney/settings/local.dist`` to ``mymoney/settings/local.py`` and
  edit it.

Internationalization
--------------------

1. copy ``mymoney/settings/l10n.dist`` to ``mymoney/settings/l10n.py`` and
   edit it.

2. edit your final setting file to use the l10n configuration instead::

    # from .base import *
    from .l10n import *

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
``mymoney/settings/test.dist`` to ``mymoney/settings/test.py`` and edit it.

Tox
```

You can use `Tox`_. At the project root directory without virtualenv, just
execute::

    tox

.. _`Tox`: http://tox.readthedocs.org

Behind the scene, it runs severals *testenv* for:

* `flake8`_
* `Sphinx`_
* test suites with coverage and report

.. _`flake8`: http://flake8.readthedocs.org
.. _`Sphinx`: http://sphinx-doc.org

Manually
````````

1. install dependencies::

    pip install -r requirements/test.txt

2. then execute tests::

    ./manage.py test --settings=mymoney.settings.test mymoney
