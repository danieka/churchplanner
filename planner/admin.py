from django.contrib import admin
from models import *

class ParticipationAdmin(admin.ModelAdmin):
	list_filter = ("user", "event")

admin.site.register(Occurrence)
admin.site.register(Token)
admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(Role)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Document)