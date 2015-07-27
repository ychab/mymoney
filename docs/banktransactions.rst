Bank transactions
=================

Once bank accounts, tags, and schedulers are created, you could now begins to
create other bank transactions. You can manage bank transactions from the
related bank account page overview:

* add
* edit
* delete

On the bank account page, you can filter bank transactions. But also apply some
actions in bulk by checking the corresponding boxes:

* reconciled selected bank transactions
* unreconciled selected bank transactions
* delete

Bank transactions alter the bank account balance when they are:

* created
* updated
* deleted

If you don't want to apply these alterations, you may set the bank
transaction's status to *inactive*. See :ref:`banktransactions-fields-status`.

Fields
------

Some fields need more explanations:

.. _banktransactions-fields-status:

Status
``````

Each statuses may have the following actions:

+---------------+---------------+---------------+
| Status        | Alter balance | Statistics    |
+===============+===============+===============+
| active        | Yes           | Yes           |
+---------------+---------------+---------------+
| ignored       | Yes           | No            |
+---------------+---------------+---------------+
| inactive      | No            | No            |
+---------------+---------------+---------------+

Indeed, bank transactions could:

* alter the bank account balance. Thus, they are used for the total of the
  balance (future, current, reconciled)
* being used for statistics (ratio and trendtime)

*Active* is the default status.
*Ignored* could be used for internal transfer for example. You may need it if
you want to alter the bank account balance but don't want to pollute your
statistics with.
*Inactive* exists just for purpose, I didn't find any use cases for it now.
Maybe changed/removed in the future.

Reconcile flag
``````````````

This is a marker which indicate whether it is synchronous with your real bank
account. It is usefull to anticipate expenses for example. You can see a quick
summary of the reconciled balance as well as the total reconciled balance. On
the contrary, you can also see the balance from a given bank transaction or the
future total balance.
