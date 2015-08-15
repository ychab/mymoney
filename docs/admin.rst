Back-office
===========

Anytime, remember that if you need to bypass the default UI, you could still
use the default Django back-office, reachable at ``/admin`` (by default) with
a staff or superuser account.

.. note:: You can modify the setting ``ADMIN_BASE_URL`` to an other
   value than *admin* for obvious security reason.

.. warning:: With the production setting template, the ``ADMIN_BASE_URL`` is
   intentionally set to an empty value to throw a CRITICAL check messages when
   the following command is run ``./manage.py check --deploy``.
