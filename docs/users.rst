Users
=====

Create a basic user
```````````````````

To don't mix superuser and basic user permissions, you will need to create and
use **only** a *basic* user. Otherwise, if you use the superuser account on
front-office and try to create a bank account, you won't see your own account
in the owner list.

..  note:: This is intentional : a basic user cannot add super user or staff
    user as an owner of a bank account.

1. create the superuser if not already::

    ./manage.py createsuperuser

2. connect to the Django backoffice at ``/admin`` in order to create a user
account.

.. warning:: Don't forgot to assign any permissions required (i.e: beginning
   with *bank*).

Permissions
```````````

Each permissions are derived from the default Django model (add, change,
delete). However, here is additionals permissions:

* administer owners: allow user to manager owners of a bank account

Anonymous user
``````````````

Because being authenticated is required, an anonymous user could **only**
access the ``/login`` url (``LOGIN_URL``). Any attempt as an anonymous user to
access an another url would redirect on the login page.