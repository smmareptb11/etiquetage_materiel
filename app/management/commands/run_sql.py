# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
import os

class Command(BaseCommand):
	"""
	Exécute les requêtes SQL présentes dans le répertoire app/sql/views afin
	de finaliser l'initialisation de la base de données du projet.
	"""

	def handle(self, *args, **options):
		directory = settings.BASE_DIR / "app/sql/views"
		with connection.cursor() as cursor:
			files = sorted(os.listdir(directory))
			for file in files:
				path = os.path.join(directory, file)
				if os.path.isfile(path):
					f = open(path, "r")
					sql = f.read()
					cursor.execute(sql)
					self.stdout.write(self.style.SUCCESS(path))