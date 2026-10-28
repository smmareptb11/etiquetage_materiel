# -*- coding: utf-8 -*-

from ..models import TMat, TMtt
from datetime import datetime
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

class MatForm(forms.ModelForm):
	"""
	Gère le formulaire de création et de mise à jour d'un matériel.
	"""

	# ========================================================================
	# CHAMPS
	# ========================================================================

	ajax = forms.CharField(
		required=False,
		widget=forms.HiddenInput
	)

	# ========================================================================
	# MÉTHODES
	# ========================================================================

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Restreint la sélection des types de matériel à ceux gérés par
		# l'utilisateur connecté lorsque celui-ci n'est pas superutilisateur
		iUti = self.request.user
		if iUti.is_authenticated and not iUti.is_superuser:
			self.fields["MTT_ID"].queryset = (
				self.fields["MTT_ID"].queryset
				.filter(tacc__UTI_ID=iUti, tacc__ACC_DROIT="W")
			)

	def clean_ajax(self):
		# Renvoie systématiquement une erreur pour toute requête AJAX afin
		# d'empêcher une soumission involontaire du formulaire
		if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
			raise ValidationError("ajax")
		return self.cleaned_data["ajax"]

class MtpForm(forms.ModelForm):
	"""
	Gère le formulaire de liaison entre une propriété et un matériel.
	"""
	
	# ========================================================================
	# MÉTHODES
	# ========================================================================

	def __init__(self, *args, request, **kwargs):
		super().__init__(*args, **kwargs)

		# Restreint la sélection des propriétés à celles associées au type de
		# matériel sélectionné
		vMttId = None
		if request.method == "POST":
			vMttId = request.POST.get("MTT_ID") or None
		else:
			iMat = request.parent_obj
			if iMat:
				vMttId = iMat.MTT_ID.pk
		self.fields["MTP_ID"].queryset = (
			self.fields["MTP_ID"].queryset.filter(MTT_ID__pk=vMttId)
		)

	def clean_DEC_VALEUR(self):
		data = self.cleaned_data
		vMtpId = data.get("MTP_ID")
		vDecValeur = data["DEC_VALEUR"]

		# Vérifie la compatibilité de la valeur renseignée avec le type de
		# données attendu par la propriété
		if vMtpId:
			vMtpTypeData = vMtpId.MTP_TYPE_DATA
			vMtpTypeDataDisplay = vMtpId.get_MTP_TYPE_DATA_display()
			try:
				match vMtpTypeData:
					case "integer":
						int(vDecValeur)
					case "decimal":
						float(vDecValeur)
					case "boolean":
						if vDecValeur not in ("1", "0"):
							raise ValueError
					case "date":
						datetime.strptime(vDecValeur, "%d/%m/%Y")
					case "datetime":
						datetime.strptime(vDecValeur, "%d/%m/%Y %H:%M")
					case _:
						pass
			except:
				raise ValidationError(
					f"La valeur saisie n'est pas compatible avec le type de "
					f"données attendu : {vMtpTypeDataDisplay}."
				)

		return vDecValeur

class MtpInline(admin.TabularInline):
	"""
	Configure les formulaires des propriétés associables à un matériel.
	"""

	extra = 0
	fields = ["MTP_ID", "DEC_VALEUR"]
	form = MtpForm
	model = TMat.MTP.through
	verbose_name = "Propriété"
	verbose_name_plural = "Propriétés"

	# ========================================================================
	# MÉTHODES
	# ========================================================================

	def _has_write_permission(self, request):
		"""
		Vérifie si l'utilisateur connecté dispose des droits d'écriture sur
		les matériels.
		"""

		iUti = request.user
		return (
			iUti.is_authenticated
			and iUti.tacc_set.filter(ACC_DROIT="W").exists()
		)

	def get_formset(self, request, obj=None, **kwargs):
		# Transfère le type de matériel sélectionné dans le formset depuis
		# l'objet parent ou les données POST
		request.parent_obj = obj
		FormSet = super().get_formset(request, obj, **kwargs)
		class FormSet_(FormSet):
			def get_form_kwargs(self, index):
				kwargs = super().get_form_kwargs(index)
				kwargs["request"] = request
				return kwargs
		return FormSet_

	def has_add_permission(self, request, obj):
		if super().has_add_permission(request, obj):
			return True
		return self._has_write_permission(request)

	def has_change_permission(self, request, obj=None):
		if super().has_change_permission(request, obj):
			return True
		return self._has_write_permission(request)

	def has_delete_permission(self, request, obj=None):
		if super().has_delete_permission(request, obj):
			return True
		return self._has_write_permission(request)

	def has_view_permission(self, request, obj=None):
		if super().has_view_permission(request, obj):
			return True
		return self._has_write_permission(request)

@admin.register(TMat)
class Mat(admin.ModelAdmin):
	"""
	Configure l'interface d'administration des matériels.
	"""

	class Media:
		js = ["app/js/admin/Mat.js"]

	fields = ["MAT_NUMERO", "MTT_ID", "UTI_ID", "ajax"]
	form = MatForm
	inlines = [MtpInline]
	list_display = ["pk", "MAT_NUMERO", "MTT_ID", "UTI_ID"]
	list_filter = [
		("MTT_ID", admin.RelatedOnlyFieldListFilter),
		("UTI_ID", admin.RelatedOnlyFieldListFilter)
	]
	
	# ========================================================================
	# MÉTHODES
	# ========================================================================

	def _has_write_permission(self, request):
		"""
		Vérifie si l'utilisateur connecté dispose des droits d'écriture sur
		les matériels.
		"""

		iUti = request.user
		return (
			iUti.is_authenticated
			and iUti.tacc_set.filter(ACC_DROIT="W").exists()
		)

	def get_form(self, request, obj=None, **kwargs):
		# Transmet la requête au formulaire afin de permettre le traitement
		# des appels AJAX
		form = super().get_form(request, obj, **kwargs)
		form.request = request
		return form

	def get_queryset(self, request):
		# Restreint la liste des matériels à ceux que l'utilisateur connecté
		# est autorisé à gérer lorsqu'il n'est pas superutilisateur
		queryset = super().get_queryset(request)
		iUti = request.user
		if iUti.is_authenticated and not iUti.is_superuser:
			queryset = queryset.filter(
				MTT_ID__tacc__UTI_ID=iUti, MTT_ID__tacc__ACC_DROIT="W"
			)
		return queryset

	def has_add_permission(self, request):
		if super().has_add_permission(request):
			return True
		return self._has_write_permission(request)

	def has_change_permission(self, request, obj=None):
		if super().has_change_permission(request, obj):
			return True
		return self._has_write_permission(request)

	def has_delete_permission(self, request, obj=None):
		if super().has_delete_permission(request, obj):
			return True
		return self._has_write_permission(request)

	def has_module_permission(self, request):
		if super().has_module_permission(request):
			return True
		return self._has_write_permission(request)

	def has_view_permission(self, request, obj=None):
		if super().has_view_permission(request, obj):
			return True
		return self._has_write_permission(request)