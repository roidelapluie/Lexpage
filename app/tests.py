from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from blog.models import BlogPost
from board.models import Thread

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import NoSuchElementException
from unittest import skipIf
from django.conf import settings


class ViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_homepage(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_no_blogpost(self):
        # Remove existing blog posts
        BlogPost.objects.all().delete()

        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['post_list']), 0)

    def test_no_thread(self):
        # Remove existing threads
        Thread.objects.all().delete()

        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['thread_list']), 0)

    def test_recent_thread(self):
        # Remove existing threads
        Thread.objects.all().delete()
        thread = Thread(title='Test thread', slug='test-thread')
        thread.save()
        message = thread.post_message(User.objects.get(username='user1'), 'foo')
        message.save()

        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['thread_list']), 1)

@skipIf(not settings.SELENIUM_TESTS, 'This test does not work with traditional webserver')
class WebsocketsTests(StaticLiveServerTestCase):
    _live_server_url = 'http://127.0.0.1:%s' % settings.TESTSERVER_LISTEN_ON_PORT

    @classmethod
    def setUpClass(cls):
        super(WebsocketsTests, cls).setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
        cls.selenium.set_window_size(1280, 1024)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(WebsocketsTests, cls).tearDownClass()

    def setUp(self):
        self.login()

    def tearDown(self):
        self.logout()

    def find_link_with_icon(self, text):
        xpath = '//a[text()[contains(.,"%s")]]' % (text)
        return self.selenium.find_element_by_xpath(xpath)

    def login(self):
        self.selenium.get('%s%s' % (self._live_server_url, reverse('auth_login')))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('user1')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('user1')
        self.selenium.find_element_by_xpath('//button[text()="S\'identifier"]').click()
        WebDriverWait(self.selenium, 20).until(
            lambda driver: driver.find_element_by_xpath('//p[contains(text(),"Bienvenue user1")]'))

    def logout(self):
        lexpagiens_link = self.find_link_with_icon('Lexpagiens')
        ActionChains(self.selenium).move_to_element(lexpagiens_link).perform()
        disconnect_link = self.find_link_with_icon('Se déconnecter')
        disconnect_link.click()
        WebDriverWait(self.selenium, 2).until(
            lambda driver: driver.find_element_by_xpath('//p[text()=\'Vous êtes maintenant déconnecté de votre compte. \']'))

    def wait_for_minichat_ready(self):
        disabled_input = '//p[text()[contains(.,"Connexion...")]]'
        WebDriverWait(self.selenium, 60).until_not(
            lambda driver: driver.find_element_by_xpath(disabled_input))

    def testSameUserMessageMinichat(self):
        text_message = 'Je suis un test'
        text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
        self.wait_for_minichat_ready()
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        text_input = self.selenium.find_element_by_name("text")
        text_input.send_keys(text_message)
        text_input.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 60).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))

    def testSameUserCorrectMessageMinichat(self):
        text_message = 'Je suis un bon test'
        text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
        fix_text_message = 's/bon/mauvais'
        fixed_text_message = 'Je suis un mauvais test'
        fixed_text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % fixed_text_message
        self.wait_for_minichat_ready()
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        text_input = self.selenium.find_element_by_name("text")
        text_input.send_keys(text_message)
        text_input.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 60).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))
        text_input.send_keys(fix_text_message)
        text_input.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 60).until(
            lambda driver: driver.find_element_by_xpath(fixed_text_message_xpath))

    def testSameUserNotificationCount(self):
        text_message = '@user1 Test'
        text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
        self.wait_for_minichat_ready()
        one_notif_xpath = '//span[@class="fa fa-bell" and text()=" 1"]'
        WebDriverWait(self.selenium, 4).until(
            lambda driver: driver.find_element_by_xpath(one_notif_xpath))
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        text_input = self.selenium.find_element_by_name("text")
        text_input.send_keys(text_message)
        text_input.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 4).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))
        two_notif_xpath = '//span[@class="fa fa-bell" and text()=" 2"]'
        WebDriverWait(self.selenium, 4).until(
            lambda driver: driver.find_element_by_xpath(two_notif_xpath))

