Schedulers
==========

Even before trying to insert some bank transaction, a better approach would be
to create first bank transaction schedulers (for recurring payments for e.g).

On the page of the bank account, click on the link *Schedule* in the menu tab
links. You are redirect on the scheduler overview page. On this page, you
could:

* see a summary of periodic debit/credit
* add/edit/delete scheduler

Fields
------

Some fields need more explanations:

Period
``````

For the moment, there is two kinds of periods:

* weekly: clone bank transactions every weeks for a given date, depending on
  localization (i.e first day of week).
* monthly: clone bank transactions every months for a given date. Don't worry,
  each month is properly respected : The 2015-01-29 will be 2015-02-28 for the
  next month.

Recurrence
``````````

You can specify how many time the scheduler will be repeat with the
*recurrence* field. Leave it empty to be repeated indefinitely.
If not infinite, when 0 is reached, the scheduler is automatically deleted.

Date
````

The *date* is used to be repeated for the next corresponding period. For
example, if you have a rent every 10 of the month, you should write
a date where day is 10, and month is the **current** month (not the next
month), even if the current day is 26 for example.

.. warning:: Keep in mind that when the background task (cron) would try to
   clone a bank transaction, it will create it for the **next** date.

Start now
`````````

When you create a scheduler, you may be interesting in running it immediatly.
However be careful, it would create a new bank transaction for the **next**
period based on the date/period given. Thus, if you want to create an automatic
bank transaction for the current month, the date field must be set for the
previous month.