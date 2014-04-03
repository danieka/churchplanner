# -*- coding: utf-8 -*-
import csv, sys, os

sys.path.append("/home/daniel/Code/github/churchplanner/churchplanner/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "churchplanner.settings")

from django.contrib.auth.models import User

with open('/home/daniel/dbox/Dropbox/Mejllista.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';')
    for row in spamreader:
        new_user = User.objects.create_user(username=row[1].lower() + "." + row[0].lower(), email=row[2])
        new_user.first_name = row[1]
        new_user.last_name = row[0]
        new_user.save()
