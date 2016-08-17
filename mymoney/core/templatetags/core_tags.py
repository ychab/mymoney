from decimal import Decimal

from django import template
from django.templatetags.l10n import localize
from django.urls import resolve, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from mymoney.apps.banktransactions.models import BankTransaction
from mymoney.core.utils.l10n import get_language_upper

from ..utils.currencies import format_currency

register = template.Library()


@register.inclusion_tag('messages.html')
def display_messages(messages):
    """
    Bootstrap alert theming.
    """
    classes = {
        'success': 'success',
        'info': 'info',
        'warning': 'warning',
        'error': 'danger',
        'debug': 'info',
    }
    for message in messages:
        message.type = classes[message.tags] if message.tags and message.tags in classes else None

    return {
        'messages': messages
    }


@register.inclusion_tag('menu_action_links.html')
def menu_action_links(request):
    """
    Render hardcoded action links depending on current user permissions (i.e :
    create, etc).
    """
    links = []
    resolver = resolve(request.path)

    if resolver.view_name == 'bankaccounts:list':
        if request.user.has_perm('bankaccounts.add_bankaccount'):
            links.append({
                'href': reverse('bankaccounts:create'),
                'text': _('Add'),
            })
    elif resolver.view_name == 'banktransactiontags:list':
        if request.user.has_perm('banktransactiontags.add_banktransactiontag'):
            links.append({
                'href': reverse('banktransactiontags:create'),
                'text': _('Add'),
            })
    elif resolver.view_name in ['banktransactions:list', 'banktransactions:calendar']:
        if request.user.has_perm('banktransactions.add_banktransaction'):
            links.append({
                'href': reverse('banktransactions:create', kwargs=resolver.kwargs),
                'text': _('Add bank transaction'),
            })
        if request.user.has_perm('bankaccounts.delete_bankaccount'):
            links.append({
                'href': reverse('bankaccounts:delete', kwargs={
                    'pk': resolver.kwargs['bankaccount_pk'],
                }),
                'text': _('Delete bank account'),
            })
    elif resolver.view_name == 'banktransactionschedulers:list':  # pragma: no branch
        if request.user.has_perm('banktransactionschedulers.add_banktransactionscheduler'):
            links.append({
                'href': reverse('banktransactionschedulers:create', kwargs=resolver.kwargs),
                'text': _('Add'),
            })

    return {
        'links': links,
    }


@register.inclusion_tag('menu_item_links.html')
def menu_item_links(request):
    """
    Render hardcoded item links, which are children of tab links.
    """
    links = []
    resolver = resolve(request.path)

    if resolver.view_name in ('banktransactionanalytics:ratio',
                              'banktransactionanalytics:trendtime'):
        links = [
            {
                'href': reverse('banktransactionanalytics:ratio', kwargs={
                    'bankaccount_pk': resolver.kwargs['bankaccount_pk'],
                }),
                'text': _('Stat report'),
                'is_active': (
                    resolver.view_name == 'banktransactionanalytics:ratio'
                ),
            },
            {
                'href': reverse('banktransactionanalytics:trendtime', kwargs={
                    'bankaccount_pk': resolver.kwargs['bankaccount_pk'],
                }),
                'text': _('Trendtime report'),
                'is_active': (
                    resolver.view_name == 'banktransactionanalytics:trendtime'
                ),
            },
        ]
    elif resolver.view_name in ('banktransactions:list',
                                'banktransactions:calendar'):
        links = [
            {
                'href': reverse('banktransactions:list', kwargs={
                    'bankaccount_pk': resolver.kwargs['bankaccount_pk'],
                }),
                'text': _('Table view'),
                'is_active': (
                    resolver.view_name == 'banktransactions:list'
                ),
            },
            {
                'href': reverse('banktransactions:calendar', kwargs={
                    'bankaccount_pk': resolver.kwargs['bankaccount_pk'],
                }),
                'text': _('Calendar view'),
                'is_active': (
                    resolver.view_name == 'banktransactions:calendar'
                ),
            },
        ]

    return {
        'links': links,
    }


@register.inclusion_tag('menu_tab_links.html')
def menu_tab_links(request):
    """
    Render hardcoded tab links depending on current user permissions.
    """
    links = []
    resolver = resolve(request.path)

    bankaccount_pk = resolver.kwargs['pk'] if 'pk' in resolver.kwargs else resolver.kwargs['bankaccount_pk']

    links.append({
        'href': reverse('banktransactions:list', kwargs={
            'bankaccount_pk': bankaccount_pk
        }),
        'text': _('See'),
        'glyph': 'eye-open',
        'is_active': resolver.view_name == 'banktransactions:list'
    })

    if request.user.has_perm('bankaccounts.change_bankaccount'):
        links.append({
            'href': reverse('bankaccounts:update', kwargs={
                'pk': bankaccount_pk
            }),
            'text': _('Edit'),
            'glyph': 'edit',
            'is_active': resolver.view_name == 'bankaccounts:update'
        })

    links.append({
        'href': reverse('banktransactionschedulers:list', kwargs={
            'bankaccount_pk': bankaccount_pk
        }),
        'text': _('Scheduler'),
        'glyph': 'time',
        'is_active': resolver.view_name == 'banktransactionschedulers:list'
    })

    links.append({
        'href': reverse('banktransactionanalytics:ratio', kwargs={
            'bankaccount_pk': bankaccount_pk
        }),
        'text': _('Statistics'),
        'glyph': 'stats',
        'is_active': resolver.view_name in [
            'banktransactionanalytics:ratio',
            'banktransactionanalytics:trendtime',
            'banktransactionanalytics:ratiosummary',
            'banktransactionanalytics:trendtimesummary',
        ],
    })

    return {
        'links': links,
    }


@register.inclusion_tag('payment_method.html')
def payment_method(value):
    """
    Theming output of payment methods.
    """
    maps = {
        BankTransaction.PAYMENT_METHOD_CREDIT_CARD: {
            'glyph': 'credit-card',
            'text': _('Credit card'),
        },
        BankTransaction.PAYMENT_METHOD_CASH: {
            'glyph': 'usd',
            'text': _('Cash'),
        },
        BankTransaction.PAYMENT_METHOD_TRANSFER: {
            'glyph': 'transfer',
            'text': _('Transfer'),
        },
        BankTransaction.PAYMENT_METHOD_TRANSFER_INTERNAL: {
            'glyph': 'resize-horizontal',
            'text': _('Internal transfer'),
        },
        BankTransaction.PAYMENT_METHOD_CHECK: {
            'glyph': 'envelope',
            'text': _('Check'),
        },
    }

    return maps[value]


@register.inclusion_tag('breadcrumb.html')
def breadcrumb(request, bankaccount_pk=None):
    links = []
    resolver = resolve(request.path)

    if bankaccount_pk is None:
        bankaccount_pk = resolver.kwargs['bankaccount_pk']

    if resolver.view_name in ("banktransactionschedulers:create",
                              "banktransactionschedulers:update"):
        links.append({
            'href': reverse("banktransactions:list", kwargs={
                "bankaccount_pk": bankaccount_pk,
            }),
            'text': _('Bank account'),
        })
        links.append({
            'href': reverse("banktransactionschedulers:list", kwargs={
                "bankaccount_pk": bankaccount_pk,
            }),
            'text': _("Schedulers"),
        })

    elif resolver.view_name in ("banktransactions:create",  # pragma: no branch
                                "banktransactions:update"):
        links.append({
            'href': reverse("banktransactions:list", kwargs={
                "bankaccount_pk": bankaccount_pk,
            }),
            'text': _('Bank account'),
        })

    return {
        "links": links,
    }


@register.filter
def language_to_upper(lang):
    """
    Force language given to be uppercase.
    """
    return get_language_upper(lang)


@register.filter
def merge_form_errors(form):
    """
    Combine all form errors (except hidden) into one list.
    """
    errors = list(form.non_field_errors())

    for field in form.visible_fields():
        errors += field.errors

    return errors


@register.filter
def form_errors_exists(form, code):
    """
    Check that a given code error form exists.
    """
    for error in form.non_field_errors().as_data():
        if error.code == code:
            return True

    return False


@register.filter
def currency_positive(amount, currency):
    """
    Format an amount with its currency and force positive prefix.
    """
    prefix = '+' if Decimal(amount) > 0 else ''
    return prefix + format_currency(amount, currency)


@register.filter
def localize_positive(val):
    """
    Localize a number and force positive prefix.
    """
    prefix = '+' if Decimal(val) > 0 else ''
    return prefix + localize(val)


@register.filter()
def localize_positive_color(val):
    """
    Wrap a localize Decimal into a text with appropriate color.
    """
    localized = localize_positive(val)
    type = 'success' if Decimal(val) >= 0 else 'danger'
    return mark_safe('<p class="text-' + type + '">' + localized + '</p>')
