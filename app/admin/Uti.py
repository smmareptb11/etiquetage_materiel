# -*- coding: utf-8 -*-

from ..models import TUti
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

@admin.register(TUti)
class Uti(UserAdmin):
	"""
	Configure l'interface d'administration des utilisateurs.
	"""

	add_fieldsets = [
		(None, {"fields" : [
			"username", "usable_password", "password1", "password2"
		]}),
		("Informations personnelles", {"fields": ["first_name", "last_name"]})
	]
	fieldsets = [
		(None, {"fields" : ["username", "password"]}),
		("Informations personnelles", {"fields": [
			"first_name", "last_name", "email"
		]}),
		("Permissions", {"fields": ["is_active", "is_staff", "is_superuser"]})
	]
	list_display = [
		"pk",
		"username",
		"first_name",
		"last_name",
		"is_active",
		"is_staff",
		"is_superuser"
	]
	list_filter = ["is_active", "is_staff", "is_superuser"]
	ordering = []
	search_fields = ["username", "first_name", "last_name"]