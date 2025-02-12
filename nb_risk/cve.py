from netbox.plugins.utils import get_plugin_config
from dcim.models import Device, Site, DeviceType
from tenancy.models import Tenant
from virtualization.models import VirtualMachine

from utilities.views import ViewTab, register_model_view
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from django.views.generic import View
from django.shortcuts import redirect, render

from utilities.views import ObjectPermissionRequiredMixin
from utilities.permissions import get_permission_for_model

import logging
import requests

logger = logging.getLogger(__name__)

from . import forms, models, tables

# Vulnerability Search Views


class VulnerabilitySearchView(ObjectPermissionRequiredMixin, View):
    queryset = models.Vulnerability.objects.all()
    template_name = "nb_risk/vulnerability_search.html"
    tab = None
    filterset_form = forms.VulnerabilitySearchFilterForm

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, "view")

    def get(self, request, **kwargs):

        cves = get_cves(request)
        table = tables.CveTable(cves)

        return render(
            request,
            self.template_name,
            {
                "tab": self.tab,
                "cves": cves,
                "filter_form": self.filterset_form,
                "table": table,
            },
        )

def get_query(request):
    if request.GET.get("cpe") is not None:
        return {
            "URI" : "https://services.nvd.nist.gov/rest/json/cpes/2.0",
            "payload":  {"cpeName": request.GET.get("cpe") } 
        }
    elif request.GET.get("cve") is not None:
        return {
            "URI" : "https://services.nvd.nist.gov/rest/json/cves/2.0",
            "payload": { "cveId" : request.GET.get("cve") }
        }
    elif request.GET.get("keyword") is not None:
        return {
            "URI" : "https://services.nvd.nist.gov/rest/json/cves/2.0",
            "payload": { "keywordSearch" : request.GET.get("keyword") }
        }
    elif request.GET.get("device_type") is not None:
        device_type_id = request.GET.get("device_type")
        device_type = DeviceType.objects.get(id=device_type_id)
        manufactor = device_type.manufacturer.name
        product = device_type.model
        version = request.GET.get("version")
        if version is None:
            version = "-"
        if request.GET.get("part") is not None:
            part = request.GET.get("part")
        else:
            part = "h"
        query = f"cpe:2.3:{part}:{manufactor}:{product}:{version}:*:*:*:*:*:*:*"
        return {
            "URI" : "https://services.nvd.nist.gov/rest/json/cpes/2.0",
            "payload": {"cpeName": f"{query}"}
        }
        

def get_cves(request):
    query = get_query(request)
    if query is None:
        return []
    try:
        proxies = get_plugin_config("nb_risk", "proxies")
        r = requests.get(
            query["URI"], params=query["payload"], proxies=proxies
        )
        r.raise_for_status()
        output = []
        for entry in r.json()["vulnerabilities"]:
            cve = {"id": entry["cve"]["id"]}
            for description in entry["cve"]["descriptions"]:
                if description["lang"] == "en":
                    cve["description"] = description["value"]
                    break
            for metric in entry["cve"]["metrics"]:
                if metric == "cvssMetricV2":
                    metrics = entry["cve"]["metrics"][metric][0]["cvssData"]
                    attributes = ['accessVector', 'accessComplexity', 'authentication', 'confidentialityImpact', 'integrityImpact', 'availabilityImpact', 'baseScore']
                    for attribute in attributes:
                        if attribute in metrics:
                            cve[attribute] = metrics[attribute]
                        else:
                            cve[attribute] = ""
            return_url = f"{request.path}?{request.META['QUERY_STRING']}"
            cve["return_url"] = return_url
            output.append(cve)
        return output
    except Exception as e:
        print(e)
        return []
