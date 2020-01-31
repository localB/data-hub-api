from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy
from django.views.decorators.csrf import csrf_protect
from rest_framework import serializers

from datahub.company.admin.utils import (
    AdminException,
    format_company_diff,
    redirect_with_message,
)
from datahub.dnb_api.link_company import (
    CompanyAlreadyDNBLinkedException,
    link_company_with_dnb,
)
from datahub.dnb_api.utils import (
    DNBServiceConnectionError,
    DNBServiceError,
    DNBServiceInvalidRequest,
    DNBServiceInvalidResponse,
    DNBServiceTimeoutError,
    get_company,
)


@redirect_with_message
@method_decorator(csrf_protect)
def dnb_link_review_changes(model_admin, request):
    """
    View to allow users to review changes that would be applied to a record before linking it.
    POSTs make the link and redirect the user to view the updated record.
    """
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    dh_company = model_admin.get_object(request, request.GET.get('company'))
    duns_number = request.GET.get('duns_number')

    if not (dh_company and duns_number):
        raise SuspiciousOperation()

    company_list_page = reverse(
        admin_urlname(model_admin.model._meta, 'changelist'),
    )
    is_post = request.method == 'POST'

    if is_post:
        try:
            link_company_with_dnb(dh_company.pk, duns_number, request.user)
        except CompanyAlreadyDNBLinkedException as exc:
            raise AdminException(str(exc), company_list_page)
        except serializers.ValidationError:
            message = 'Data from D&B did not pass the Data Hub validation checks.'
            raise AdminException(message, company_list_page)

        messages.add_message(request, messages.SUCCESS, 'Company linked to D&B successfully.')
        company_change_page = reverse(
            admin_urlname(model_admin.model._meta, 'change'),
            kwargs={'object_id': dh_company.pk},
        )
        return HttpResponseRedirect(company_change_page)

    try:
        dnb_company = get_company(duns_number)

    except (
        DNBServiceError,
        DNBServiceConnectionError,
        DNBServiceTimeoutError,
        DNBServiceInvalidResponse,
    ):
        message = 'Something went wrong in an upstream service.'
        raise AdminException(message, company_list_page)

    except DNBServiceInvalidRequest:
        message = 'No matching company found in D&B database.'
        raise AdminException(message, company_list_page)

    return TemplateResponse(
        request,
        'admin/company/company/update-from-dnb.html',
        {
            **model_admin.admin_site.each_context(request),
            'media': model_admin.media,
            'opts': model_admin.model._meta,
            'title': gettext_lazy('Confirm Link Company with D&B'),
            'diff': format_company_diff(dh_company, dnb_company),
        },
    )
