# -*- coding: utf-8 -*-

from .models import TMat
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

class MatDetailJson(LoginRequiredMixin, View):
	"""
	Permet la consultation des informations détaillées d'un matériel au format
	JSON.
	"""
	
	def get(self, request, *args, **kwargs):

		# Affiche la vue associée lorsque le matériel est reconnu, sinon
		# retourne une erreur HTTP 404
		iUti = request.user
		ks = {"pk": kwargs["vMatId"]}
		if iUti.is_authenticated and not iUti.is_superuser:
			ks["MTT_ID__UTI"] = iUti
		iMat = get_object_or_404(TMat, **ks)

		iUti = iMat.UTI_ID
		iUtiView = iUti.vuti if iUti else None

		# Initialise les données au format JSON
		data = {
			"Numéro du matériel": iMat.MAT_NUMERO,
			"Type de matériel": iMat.MTT_ID.MTT_LIBELLE,
			"Bénéficiaire": iUtiView.UTI_NOM if iUtiView else "",
			"Bénéficiaire (UID)": iUtiView.UTI_UID if iUtiView else ""
		}

		# Complète les données JSON avec les valeurs typées des propriétés
		# décrivant le matériel
		for iDec in iMat.tdec_set.select_related("MTP_ID"):
			vDecValeur = iDec.DEC_VALEUR
			vMtpLibelle = iDec.MTP_ID.MTP_LIBELLE
			vMtpTypeData = iDec.MTP_ID.MTP_TYPE_DATA
			try:
				match vMtpTypeData:
					case "integer":
						data[vMtpLibelle] = int(vDecValeur)
					case "decimal":
						data[vMtpLibelle] = float(vDecValeur)
					case "boolean":
						if vDecValeur == "1":
							data[vMtpLibelle] = True
						elif vDecValeur == "0":
							data[vMtpLibelle] = False
						else:
							raise ValueError
					case "date":
						data[vMtpLibelle] = (
							datetime.strptime(vDecValeur, "%d/%m/%Y").date()
						)
					case "datetime":
						dt = datetime.strptime(vDecValeur, "%d/%m/%Y %H:%M")
						dt = (
							timezone
							.make_aware(dt, timezone.get_current_timezone())
						)
						data[vMtpLibelle] = dt
					case _:
						data[vMtpLibelle] = vDecValeur
			except:
				pass

		return JsonResponse(data)