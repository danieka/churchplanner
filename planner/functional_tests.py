from selenium import webdriver
from django.test import LiveServerTestCase, TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import datetime
from planner.models import Participation, Event, Occurrence, EventType, Role
from django.contrib.auth.models import User
import pytz
import time
tz = pytz.timezone("Europe/Stockholm")


def event(date):
    e = Event.objects.create(title="TestEvent", event_type=EventType.objects.get(name="Gudstjänst"))
    e.event =  Occurrence.objects.create(start_time = tz.localize(date))
    Participation.objects.create(user = User.objects.get(pk=2), event = e, attending = "true", role = Role.objects.get(name = "Mötesledare"))
    Participation.objects.create(user = User.objects.get(pk=3), event = e, attending = "null", role = Role.objects.get(name = "Textläsare"))
    e.save()

def login(browser):
	browser.find_element_by_id('id_username').send_keys("admin")
	browser.find_element_by_id('id_password').send_keys("1234")
	browser.find_element_by_id('id_submit').click()

class BasicTest(StaticLiveServerTestCase):
	fixtures = ["fixture1.json"]
	
	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(3)

	def tearDown(self):
		self.browser.quit()

	def test_login(self):
		self.browser.get(self.live_server_url)
		assert "Planering" in self.browser.title
		login(self.browser)
		menu = self.browser.find_element_by_id('main-menu').text
		assert 'Nytt evenemang' in menu
		assert 'Tabellvy' in menu

	def test_event_is_displayed(self):
		event(datetime.datetime.now() + datetime.timedelta(days = 17))
		self.browser.get(self.live_server_url)
		login(self.browser)
		t  = self.browser.find_element_by_id("table-scroll").text
		time.sleep(10)
		print(t)
		assert 'Testevenemang' in t

if __name__ == '__main__':
    unittest.main()