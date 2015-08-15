Statistics
==========

You can check statistics for a given bank account. To do so, go on the bank
account page and click on the menu tab item *Statistics*.
You can then switch between two view modes:

* ratio report: based on tags
* trendtime report: based on dates

Each report provides some basic filters and a quick summary. Each summary has
more details when you click on a targeted item.

Ratio
`````

Filter type: sum or single
++++++++++++++++++++++++++

Ratio statistics display results grouped by tags. To have relevant percentage,
numbers compared must be of the same sign (positive or negative). That's why
there is two *sub-types*:

* expenses
* wages

For an expense search with *single* mode, **each negative bank transactions**
are used.
For an expenses search with *sum* mode, **each negative sum** of tags are used.

For example, imagine you do some shopping for $100. Unfortunetely, you discover
that an item isn't good. You return it and get a refund of $25.
With *single* type filter, the amount used would be -$100. Whereas with *sum*
type filter, the amount used would be -100 + 25 = -$75.

Most of the time, the desired mode should be *sum*, that's why this is the
default mode.
