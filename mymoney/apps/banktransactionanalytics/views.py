import datetime
import json
import random

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Max, Min, QuerySet, Sum
from django.urls import reverse
from django.utils import formats
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views import generic

from mymoney.apps.banktransactions.mixins import BankTransactionAccessMixin
from mymoney.apps.banktransactions.models import BankTransaction
from mymoney.apps.banktransactiontags.models import BankTransactionTag
from mymoney.core.iterators import DateIterator
from mymoney.core.paginators import DatePaginator
from mymoney.core.utils.dates import get_date_ranges

from .forms import RatioForm, TrendtimeForm
from .mixins import RatioViewMixin, TrendTimeViewMixin


class RatioView(BankTransactionAccessMixin, RatioViewMixin, generic.FormView):

    template_name = 'banktransactionanalytics/ratio/overview.html'
    form_class = RatioForm

    def get_initial(self):
        initial = super(RatioView, self).get_initial()
        initial.update(self.session_data.get('filters', {}))
        initial.update(self.session_data.get('raw_input', {}))
        return initial

    def get_form_kwargs(self):
        kwargs = super(RatioView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        self.success_url = reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
        })
        return super(RatioView, self).get_success_url()

    def post(self, request, *args, **kwargs):

        # Skip any validations for reset action.
        if request.POST.get('reset', False):
            return self.form_valid(self.get_form())

        return super(RatioView, self).post(request, *args, **kwargs)

    def form_valid(self, form):

        if 'filter' in self.request.POST:
            filters, raw_input = {}, {}
            session_data = self.session_data

            for key, value in form.cleaned_data.items():
                value = list(value) if isinstance(value, QuerySet) else value

                if value in form.fields[key].empty_values:
                    continue

                if key == 'tags':
                    data = [tag.pk for tag in value]
                elif key.startswith('date_') or key.startswith('sum_'):
                    data = str(value)
                    raw_input[key] = self.request.POST.get(key, None)
                else:
                    data = value

                filters[key] = data

            session_data['filters'] = filters
            session_data['raw_input'] = raw_input
            self.session_data = session_data

        elif 'reset' in self.request.POST:  # pragma: no branch
            del self.session_data

        return super(RatioView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(RatioView, self).get_context_data(**kwargs)
        context['bankaccount'] = self.bankaccount

        session_data = self.session_data
        filters = session_data.get('filters', {})
        session_data['colors'] = session_data.get('colors', {})

        # Filters are required to prevent huge data aggregation costs.
        context['has_filters'] = bool(filters)
        if context['has_filters']:

            total = self.total_queryset
            if total is not None:
                colors = self.colors.copy()

                rows, sub_total = [], 0
                for data in self.tag_queryset:
                    tag_id = str(data['tag']) if data['tag'] else '0'

                    if tag_id in session_data['colors']:
                        color = session_data['colors'][tag_id]
                    else:
                        color = colors.pop(colors.index(random.choice(colors)))
                        session_data['colors'][tag_id] = color
                        self.session_data = session_data

                    rows.append({
                        'tag_id': data['tag'],
                        'tag_name': data['tag__name'],
                        'sum': data['sum'],
                        'count': data['count'],
                        'percentage': round(data['sum'] * 100 / total, 2),
                        'color': color,
                        'color_rgba': 'rgba({r}, {g}, {b}, {a})'.format(
                            r=color[0],
                            g=color[1],
                            b=color[2],
                            a=0.7,
                        ),
                    })

                    sub_total += data['sum']

                context['rows'] = rows
                context['sub_total'] = sub_total
                context['total'] = total

                if rows:
                    context['chart_data'] = json.dumps({
                        'data': [
                            {
                                'label': row['tag_name'] if row['tag_name'] else _('no tag'),
                                'value': float(row['percentage']),
                                'color': row['color_rgba'],
                                'highlight': 'rgba({r}, {g}, {b}, {a})'.format(
                                    r=row['color'][0],
                                    g=row['color'][1],
                                    b=row['color'][2],
                                    a=0.6,
                                ),
                            } for row in rows
                        ],
                        'type': filters['chart'],
                    })

        return context

    @cached_property
    def base_queryset(self):

        qs = super(RatioView, self).base_queryset

        filters = self.session_data.get('filters', {})
        if filters['type'] in (RatioForm.SUM_CREDIT, RatioForm.SUM_DEBIT):

            qs = qs.values('tag', 'tag__name')
            qs = qs.annotate(sum=Sum('amount'))

            if filters['type'] == RatioForm.SUM_CREDIT:
                qs = qs.filter(sum__gt=0)
            else:
                qs = qs.filter(sum__lt=0)

        return qs

    @property
    def total_queryset(self):

        filters = self.session_data.get('filters', {})
        if filters['type'] in (RatioForm.SINGLE_CREDIT, RatioForm.SINGLE_DEBIT):
            field = 'amount'
        else:
            field = 'sum'

        return self.base_queryset.aggregate(total=Sum(field))['total']

    @property
    def tag_queryset(self):
        qs = self.base_queryset

        filters = self.session_data.get('filters', {})

        if 'tags' in filters:
            qs = qs.filter(tag__in=filters['tags'])

        # Always group result by tags.
        if filters['type'] in (RatioForm.SINGLE_CREDIT, RatioForm.SINGLE_DEBIT):
            qs = qs.values('tag', 'tag__name')
            qs = qs.annotate(sum=Sum('amount'))

        qs = qs.annotate(count=Count('id'))

        if 'sum_min' in filters and 'sum_max' in filters:
            qs = qs.filter(sum__range=(
                filters['sum_min'],
                filters['sum_max'],
            ))
        elif 'sum_min' in filters:
            qs = qs.filter(sum__gte=filters['sum_min'])
        elif 'sum_max' in filters:
            qs = qs.filter(sum__lte=filters['sum_max'])

        if filters['type'] in (RatioForm.SINGLE_DEBIT, RatioForm.SUM_DEBIT):
            qs = qs.order_by('sum')
        else:
            qs = qs.order_by('-sum')

        return qs

    @cached_property
    def colors(self):
        return [
            [66, 139, 202],     # some kind of blue
            [128, 0, 128],      # purle
            [265, 165, 0],      # orange
            [192, 192, 192],    # silver
            [0, 128, 0],        # green
            [250, 128, 114],    # saumon
            [255, 215, 0],      # gold
            [255, 0, 0],        # red
            [64, 224, 208],     # turquoise
            [182, 128, 128],    # gray
            [255, 255, 0],      # yellow
            [128, 0, 0],        # maroon
            [128, 128, 0],      # olive
            [255, 0, 255],      # fuchsia
            [0, 255, 0],        # lime
            [0, 128, 128],      # teal
            [0, 128, 128],      # navy
            [255, 192, 203],    # pink
            [245, 222, 179],    # wheat
            [173, 216, 230],    # lightblue
            [0, 255, 255],      # aqua
            [220, 20, 60],      # crimson
        ]


class RatioSummaryView(BankTransactionAccessMixin, RatioViewMixin,
                       generic.TemplateView):

    template_name = 'banktransactionanalytics/ratio/summary/index.html'

    def dispatch(self, request, *args, **kwargs):

        if not self.session_data.get('filters', {}):
            raise PermissionDenied

        # Check that current user is owner of the given tag. Group by ids
        # manually to cache query.
        tags = BankTransactionTag.objects.get_user_tags_queryset(request.user)
        tag_id = int(self.kwargs['tag_id'])
        if tag_id != 0 and tag_id not in [tag.pk for tag in tags]:
            raise PermissionDenied

        return super(RatioSummaryView, self).dispatch(
            request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):

        if self.request.is_ajax():
            self.template_name = 'banktransactionanalytics/ratio/summary/body.html'

        return super(RatioSummaryView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(RatioSummaryView, self).get_context_data(**kwargs)
        context['bankaccount'] = self.bankaccount

        qs = self.base_queryset
        tag_id = int(kwargs['tag_id'])
        if tag_id > 0:
            qs = qs.filter(tag__pk=tag_id)
        else:
            qs = qs.filter(tag__isnull=True)
        banktransactions = qs.order_by('date')

        total = 0
        for banktransaction in banktransactions:
            total += banktransaction.amount

        context['banktransactions'] = banktransactions
        context['total'] = total

        return context


class TrendTimeView(BankTransactionAccessMixin, TrendTimeViewMixin,
                    generic.FormView):

    template_name = 'banktransactionanalytics/trendtime/overview.html'
    form_class = TrendtimeForm

    def get_initial(self):
        initial = super(TrendTimeView, self).get_initial()
        initial.update(self.session_data.get('filters', {}))
        initial.update(self.session_data.get('raw_input', {}))
        return initial

    def get_success_url(self):
        self.success_url = reverse('banktransactionanalytics:trendtime', kwargs={
            'bankaccount_pk': self.bankaccount.pk,
        })
        return super(TrendTimeView, self).get_success_url()

    def post(self, request, *args, **kwargs):

        # Skip any validations for reset action.
        if request.POST.get('reset', False):
            return self.form_valid(self.get_form())

        return super(TrendTimeView, self).post(request, *args, **kwargs)

    def form_valid(self, form):

        if 'filter' in self.request.POST:
            filters, raw_input = {}, {}
            for key, value in form.cleaned_data.items():

                if value in form.fields[key].empty_values:
                    continue

                if key == 'date':
                    data = str(value)
                    raw_input[key] = self.request.POST.get('date', None)
                    filters['date_kwargs'] = {
                        'year': value.year,
                        'month': value.month,
                        'day': value.day,
                    }
                else:
                    data = value

                filters[key] = data

            self.session_data = {
                'filters': filters,
                'raw_input': raw_input,
            }

        elif 'reset' in self.request.POST:  # pragma: no branch
            del self.session_data

        return super(TrendTimeView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TrendTimeView, self).get_context_data(**kwargs)
        context['bankaccount'] = self.bankaccount

        filters = self.session_data.get('filters', {})
        context['has_filters'] = bool(filters)

        if filters:

            # Get first and last bank transaction to prevent infinite pager. If
            # one is missing, it just mean that there is no data at all.
            first, last = self.get_queryset_dates_delimiters()
            if first and last:
                base_date = datetime.date(**filters['date_kwargs'])
                granularity = filters['granularity']

                if self.request.GET.get('date'):
                    try:
                        base_date = datetime.datetime.strptime(
                            self.request.GET.get('date'),
                            '%Y-%m-%d',
                        ).date()

                    except ValueError:
                        pass

                # Requested date is not out of range?
                first_range = get_date_ranges(first, granularity)[0]
                last_range = get_date_ranges(last, granularity)[1]
                if first_range <= base_date <= last_range:

                    date_start, date_end = get_date_ranges(
                        base_date,
                        granularity,
                    )

                    balance = self.get_queryset_balance(date_start)['sum'] or 0
                    balance += self.bankaccount.balance_initial
                    context['balance_initial'] = balance

                    items_qs = self.get_queryset_items(date_start, date_end)
                    items = {item['date']: item for item in items_qs}

                    # Start and end iterator at first/last bank transaction,
                    # not the range calculated.
                    iterator = DateIterator(
                        first if first > date_start else date_start,
                        last if last < date_end else date_end,
                    )
                    rows = []
                    for date_step in iterator:
                        delta = percentage = count = 0

                        # If no new bank transaction, same as previous.
                        if date_step in items:
                            delta = items[date_step]['sum']
                            percentage = (delta * 100 / balance) if balance else 0
                            balance += items[date_step]['sum']
                            count = items[date_step]['count']

                        rows.append({
                            'date': date_step,
                            'count': count,
                            'balance': balance,
                            'delta': delta,
                            'percentage': round(percentage, 2),
                        })

                    context['rows'] = rows
                    context['chart_data'] = json.dumps({
                        'data': {
                            'labels': [
                                formats.date_format(
                                    row['date'], 'SHORT_DATE_FORMAT',
                                )
                                for row in rows
                            ],
                            'datasets': [
                                {
                                    'fillColor': "rgba(66, 139, 202, 0.5)",
                                    'strokeColor': "rgba(66, 139, 202, 0.8)",
                                    'pointColor': "rgba(66, 139, 202, 0.75)",
                                    'pointHighlightFill': "#fff",
                                    'pointHighlightStroke': "rgba(66, 139, 202, 1)",
                                    'data': [
                                        float(row['balance']) for row in rows
                                    ],
                                }
                            ],
                        },
                        'type': filters['chart'],
                    })
                    paginator = DatePaginator(
                        first_range, last_range, granularity
                    )
                    context['page_obj'] = paginator.page(base_date)

        return context

    def get_queryset_dates_delimiters(self):

        dates = self.base_queryset.aggregate(
            first=Min('date'),
            last=Max('date'),
        )
        return dates['first'], dates['last']

    def get_queryset_balance(self, date_start):

        qs = self.base_queryset.filter(
            date__lt=date_start,
        ).aggregate(
            sum=Sum('amount')
        )

        return qs

    def get_queryset_items(self, date_start, date_end):

        qs = self.base_queryset.filter(
            bankaccount=self.bankaccount,
            status=BankTransaction.STATUS_ACTIVE,
            date__range=(date_start, date_end),
        )

        qs = qs.values('date')
        qs = qs.annotate(sum=Sum('amount'), count=Count('id'))
        qs = qs.order_by('date')

        return qs


class TrendTimeSummaryView(BankTransactionAccessMixin, TrendTimeViewMixin,
                           generic.TemplateView):

    template_name = 'banktransactionanalytics/trendtime/summary/index.html'

    def render_to_response(self, context, **response_kwargs):

        if self.request.is_ajax():
            self.template_name = 'banktransactionanalytics/trendtime/summary/body.html'

        return super(TrendTimeSummaryView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(TrendTimeSummaryView, self).get_context_data(**kwargs)
        context['bankaccount'] = self.bankaccount

        banktransactions = []
        try:
            base_date = datetime.date(
                int(kwargs['year']), int(kwargs['month']), int(kwargs['day']),
            )
        except ValueError:
            pass
        else:
            banktransactions = (
                self.base_queryset.filter(date=base_date).order_by('pk')
            )

        total = 0
        for banktransaction in banktransactions:
            total += banktransaction.amount

        context['banktransactions'] = banktransactions
        context['total'] = total

        return context
