# -*- coding: utf-8 -*-

from django.contrib.auth.models import AbstractUser
from django.db import models

class TAcc(models.Model):
	"""
	Représente une autorisation permettant à un utilisateur d'accéder aux
	matériels associés à un type donné.
	"""

	class Meta:
		db_table = "T_J_ACCEDE_ACC"
		ordering = ["-ACC_DROIT", "UTI_ID"]

	# ========================================================================
	# CHAMPS
	# ========================================================================

	ACC_ID = models.BigAutoField(primary_key=True)

	MTT_ID = models.ForeignKey(
		to="TMtt",
		on_delete=models.CASCADE,
		db_column="MTT_ID"
	)

	UTI_ID = models.ForeignKey(
		to="TUti",
		on_delete=models.CASCADE,
		db_column="UTI_ID",
		verbose_name="Utilisateur"
	)

	ACC_DROIT = models.CharField(
		max_length=1,
		choices=[("R", "Lecture"), ("W", "Écriture")],
		verbose_name="Droit"
	)

class TDec(models.Model):
	"""
	Représente une valeur de propriété utilisée pour décrire et caractériser
	un matériel.
	"""

	class Meta:
		db_table = "T_J_DECRIT_DEC"
		ordering = ["MTP_ID"]

	# ========================================================================
	# CHAMPS
	# ========================================================================

	DEC_ID = models.BigAutoField(primary_key=True)

	MAT_ID = models.ForeignKey(
		to="TMat",
		on_delete=models.CASCADE,
		db_column="MAT_ID"
	)

	MTP_ID = models.ForeignKey(
		to="TMtp",
		on_delete=models.CASCADE,
		db_column="MTP_ID",
		verbose_name="Propriété"
	)

	DEC_VALEUR = models.CharField(
		max_length=255,
		verbose_name="Valeur"
	)

class TMat(models.Model):
	"""
	Représente un matériel.
	"""

	class Meta:
		db_table = "T_E_MATERIEL_MAT"
		ordering = ["MAT_NUMERO"]
		verbose_name = "Matériel"
		verbose_name_plural = "Matériels"

	# ========================================================================
	# CHAMPS
	# ========================================================================

	MAT_ID = models.BigAutoField(primary_key=True)

	MAT_NUMERO = models.CharField(
		max_length=63,
		blank=True,
		help_text=(
			"Numéro interne attribué par le gestionnaire du type de matériel."
		),
		verbose_name="Numéro du matériel"
	)

	MTT_ID = models.ForeignKey(
		to="TMtt",
		on_delete=models.CASCADE,
		db_column="MTT_ID",
		verbose_name="Type de matériel"
	)

	UTI_ID = models.ForeignKey(
		to="TUti",
		on_delete=models.SET_NULL,
		blank=True,
		db_column="UTI_ID",
		null=True,
		verbose_name="Bénéficiaire"
	)

	# ========================================================================
	# RELATIONS PLUSIEURS-À-PLUSIEURS
	# ========================================================================

	MTP = models.ManyToManyField(to="TMtp", through="TDec")

class TMtp(models.Model):
	"""
	Représente une propriété associée à un type de matériel.
	"""

	class Meta:
		db_table = "T_R_MATERIEL_PROPRIETE_MTP"
		ordering = ["MTP_RANG", "MTP_LIBELLE"]

	# ========================================================================
	# CHAMPS
	# ========================================================================

	MTP_ID = models.BigAutoField(primary_key=True)

	MTP_LIBELLE = models.CharField(
		max_length=255,
		verbose_name="Libellé"
	)

	MTP_RANG = models.PositiveBigIntegerField(
		default=0,
		verbose_name="Ordre d'affichage"
	)

	MTP_TYPE_DATA = models.CharField(
		max_length=63,
		choices=[
			("string", "Texte"),
			("integer", "Nombre entier"),
			("decimal", "Nombre décimal"),
			("boolean", "Booléen"),
			("date", "Date"),
			("datetime", "Date et heure")
		],
		verbose_name="Type de données de la valeur"
	)

	MTT_ID = models.ForeignKey(
		to="TMtt",
		on_delete=models.CASCADE,
		db_column="MTT_ID"
	)

	# ========================================================================
	# MÉTHODES / PROPRIÉTÉS
	# ========================================================================

	def __str__(self):
		return self.MTP_LIBELLE

class TMtt(models.Model):
	"""
	Représente un type de matériel.
	"""

	class Meta:
		db_table = "T_R_MATERIEL_TYPE_MTT"
		ordering = ["MTT_RANG", "MTT_LIBELLE"]
		verbose_name = "Type de matériel"
		verbose_name_plural = "Types de matériel"

	# ========================================================================
	# CHAMPS
	# ========================================================================

	MTT_ID = models.BigAutoField(primary_key=True)

	MTT_LIBELLE = models.CharField(
		max_length=255,
		verbose_name="Libellé"
	)

	MTT_RANG = models.PositiveBigIntegerField(
		default=0,
		verbose_name="Ordre d'affichage"
	)

	# ========================================================================
	# RELATIONS PLUSIEURS-À-PLUSIEURS
	# ========================================================================

	UTI = models.ManyToManyField(to="TUti", through="TAcc")

	# ========================================================================
	# MÉTHODES / PROPRIÉTÉS
	# ========================================================================

	def __str__(self):
		return self.MTT_LIBELLE

class TUti(AbstractUser):
	"""
	Représente un utilisateur.
	"""

	class Meta:
		db_table = "T_E_UTILISATEUR_UTI"
		ordering = ["first_name", "last_name"]
		verbose_name = "Utilisateur"
		verbose_name_plural = "Utilisateurs"

	# ========================================================================
	# CHAMPS
	# ========================================================================

	first_name = models.CharField(
		max_length=150,
		verbose_name="Prénom"
	)

	last_name = models.CharField(
		max_length=150,
		verbose_name="Nom"
	)

	# ========================================================================
	# MÉTHODES / PROPRIÉTÉS
	# ========================================================================

	def __str__(self):
		if self.vuti is None:
			return f"{self.__class__.__name__} object ({self.pk})"
		else:
			return self.vuti.UTI_NOM

class VUti(models.Model):
	"""
	Ajoute des colonnes calculées associées à un utilisateur afin d'enrichir
	les données exposées par la vue.
	"""
	
	class Meta:
		db_table = "V_UTI"
		managed = False

	# ========================================================================
	# CHAMPS
	# ========================================================================

	UTI_ID = models.OneToOneField(
		to="TUti",
		on_delete=models.DO_NOTHING,
		db_column="UTI_ID",
		primary_key=True
	)

	UTI_NOM = models.CharField(
		max_length=301,
		blank=True
	)

	UTI_UID = models.CharField(max_length=254)