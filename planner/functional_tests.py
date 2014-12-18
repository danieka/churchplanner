from selenium import webdriver
from django.test import LiveServerTestCase

class BasicTest(LiveServerTestCase):
	fixtures = ["fixture1.json"]
	
	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(3)

	def tearDown(self):
		self.browser.quit()

	def test_login(self):
		
		self.browser.get(self.live_server_url)
		assert "Planering" in self.browser.title
		ubox = self.browser.find_element_by_id('id_username')
		pbox = self.browser.find_element_by_id('id_password')

		ubox.send_keys("admin")
		pbox.send_keys("1234")