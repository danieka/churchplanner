# -*- coding: utf-8 -*-
from planner.models import Event, EventType, Participation
import csv

def export_events(type, path):
	with open(path, 'w') as f:
		csvwriter = csv.writer(f, dialect = csv.unix_dialect)
		eventtype = EventType.objects.get(name = type)
		columns = ["Datum", "Titel"]
		for role in eventtype.roles.all():
			columns.append(role.name)
		csvwriter.writerow(columns)
		
		for event in Event.objects.filter(event_type = eventtype):
			t = [event.event.start_time.strftime("%d %B %Y"), event.title]
			for role in eventtype.roles.all():
				participations = Participation.objects.filter(event = event, role = role)
				l = []
				for participation in participations:
					l.append("%s %s" % (participation.user.first_name, participation.user.last_name))
				t.append("\n".join(l))
			csvwriter.writerow(t)