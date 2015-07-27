.. image:: https://requires.io/github/ychab/mymoney/requirements.svg?branch=master
   :target: https://requires.io/github/ychab/mymoney/requirements/?branch=master
   :alt: Requirements Status

.. image:: https://coveralls.io/repos/ychab/mymoney/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/ychab/mymoney?branch=master

MyMoney is a personal finance Web application build with the `Django`_
framework.

.. _`Django`: https://www.djangoproject.com/

The main goals of this project are to:

* follow and anticipate your bank account balance anywhere
* tag and analyse your expenses
* summarize your recurring expenses/wages

Features:

* manage bank accounts (balance, currency, owners, etc)
* manage bank transactions (debit/credit, amount, label, date, reconciled or
  not, payment method, add note, etc)
* tag bank transactions
* analyse bank transactions with graphs (timeline in weeks/months or statistics
  per tags). Use the `Chart.js`_ library.
* schedule recurrent bank transactions
* `Bootstrap`_ integration for mobile
* even if it doesn't make sense, it is multi-user!

.. _`Chart.js`: http://www.chartjs.org/
.. _`Bootstrap`: http://getbootstrap.com/

This is my first Django/Python project so:

* any technical advices/feedbacks would be *really* appreciated
* some *useless* features have been done mainly for learning and fun ;-)

For documentation, see http://mymoney.readthedocs.org/en/latest/