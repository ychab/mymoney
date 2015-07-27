from dateutil.relativedelta import relativedelta


class DateIterator(object):
    """
    Iterate over each days for a given dates range.
    """

    def __init__(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end

    def __iter__(self):
        self.date = None
        return self

    def __next__(self):

        if self.date is None:
            self.date = self.date_start
        else:
            self.date += relativedelta(days=1)

        if self.date > self.date_end:
                raise StopIteration

        return self.date
