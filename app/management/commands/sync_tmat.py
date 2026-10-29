# -*- coding: utf-8 -*-

from ...models import TDec, TMat, TMtt, TUti
from django.conf import settings
from django.core.management.base import BaseCommand
import os
import pandas as pd

class Command(BaseCommand):
	"""
	Synchronise les données des matériels d'un type donné à partir d'un
	fichier CSV conforme au format attendu.
	"""

	def add_arguments(self, parser):
		parser.add_argument("MTT_ID", type=int)
		parser.add_argument("FILE", type=str)

	def handle(self, *args, **options):

		# Définit le chemin du fichier CSV à traiter
		directory = settings.BASE_DIR / "sync"
		path = os.path.join(directory, options["FILE"])

		if os.path.isfile(path):

			# Charge le fichier CSV dans un DataFrame et remplace les valeurs
			# manquantes par des chaînes vides
			df = pd.read_csv(path, sep=";", encoding="cp1252").fillna("")

			# Parcourt chaque enregistrement du DataFrame afin de mettre à
			# jour les données en base
			for index, row in df.iterrows():

				# Met à jour les données attributaires du matériel dans la
				# base de données
				iMat = TMat.objects.get(pk=row["MAT_ID"])
				iMat.MAT_NUMERO = row["MAT_NUMERO"]
				iMat.UTI_ID = (
					TUti.objects.filter(vuti__UTI_UID=row["UTI_UID"]).first()
				)
				iMat.save()

				# Met à jour les propriétés associées au matériel dans la base
				# de données
				remove = []
				iMtt = TMtt.objects.get(pk=options["MTT_ID"])
				for iMtp in iMtt.tmtp_set.all():
					vDecValeur = row.get(iMtp.MTP_LIBELLE)
					if vDecValeur == "":
						remove.append(iMtp)
					else:
						iDec, created = TDec.objects.update_or_create(
							MAT_ID=iMat,
							MTP_ID=iMtp,
							defaults={"DEC_VALEUR": vDecValeur}
						)
				iMat.MTP.remove(*remove)

				self.stdout.write(self.style.SUCCESS(row["MAT_ID"]))