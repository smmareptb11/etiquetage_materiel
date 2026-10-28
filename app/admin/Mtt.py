# -*- coding: utf-8 -*-

from ..models import TMtp, TMtt
from django.contrib import admin

class MtpInline(admin.TabularInline):
	"""
	Configure les formulaires des propriétés associées à un type de matériel.
	"""

	extra = 0
	fields = ["MTP_LIBELLE", "MTP_TYPE_DATA", "MTP_RANG"]
	model = TMtp
	verbose_name = "Propriété"
	verbose_name_plural = "Propriétés"

class UtiInline(admin.TabularInline):
	"""
	Configure les formulaires des autorisations d'accès des utilisateurs aux
	données d'un type de matériel.
	"""

	extra = 0
	fields = ["UTI_ID", "ACC_DROIT"]
	model = TMtt.UTI.through
	verbose_name = "Autorisation d'accès"
	verbose_name_plural = "Autorisations d'accès"

@admin.register(TMtt)
class Mtt(admin.ModelAdmin):
	"""
	Configure l'interface d'administration des types de matériel.
	"""

	fields = ["MTT_LIBELLE", "MTT_RANG"]
	inlines = [MtpInline, UtiInline]
	list_display = ["pk", "MTT_LIBELLE", "MTT_RANG"]