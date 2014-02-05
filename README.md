##churchplanner

#####This isn't really for public consumption yet.

This will eventually be a web tool for planning your church's events and activites.

Rigth now everything is in Swedish so if you're interested in using this project, 
do contact me and I'll prioritize the translation. 

###Installation

Installation should be rather simple, first of you will need a lot of dependencies, all of them can be downloaded with pip:

django
django-all-access
south
pytz
django-crispy-forms
Django-facebook
celery
django-celery
wand
pil

Besides that you need libmagickwand-dev, you can try:
apt-get install libmagickwand-dev

You also need to download TokenInput: 
https://github.com/loopj/jquery-tokeninput 

Extract src and styles in static/jquery_fields/tokeninput

Last you need to install RabbitMQ, or some other celery backend if you want tasks like facebook events and mailouts.

###Configuration
In churchplanner/suggested_settings.py are the settings you can use as a starting point. The server I run
use Nginx/Gunicorn for serving static files and django. I use RabbitMQ as a celery backend. The Google-able
guides are much better than anything I can write.

Once you've got everything up and running you need to add provider of Oauth-login. Log inte your sites admin interface 
and follow the instructions here: http://django-all-access.readthedocs.org/en/v0.5.X/providers.html#facebook-example
 
Next you need to set up churchplanner to fit your organization and your workflow. Start by adding roles in the django admin. Some suggestions might be "Preacher", "Technician", "Food", "Greeter", "Piano", "Singer". Now you need to create different types of events. In your service you might need a preacher, technician and someone to greet people coming to the service. Lastly you need to add everyone who will have a task to the system. Add them as ordinary django users with first and lastname and email. No password is needed for them. Anyone who should plan must be marked as staff.

###Usage

More info coming

###Contribute

All contributions are greatly appriciated. Have a look at the issues, I always try to have some easier issues marked as bite-size so you have somewhere to start.

The test coverage is rather bad so if you're fixing a bug please add a test for that bug.

Daniel Karlsson, myfirstname.mylastname [at] roseniuskyrkan.se
