import os

from django.core.servers.basehttp import WSGIServer
from django.test.testcases import LiveServerThread, QuietWSGIRequestHandler
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.module_loading import import_string

from socketserver import ThreadingMixIn
from ws4redis.django_runserver import _websocket_url, _websocket_app, _django_app
from whitenoise.django import DjangoWhiteNoise

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

WebDriver = import_string(settings.SELENIUM_WEBDRIVER)

def GhostDriverBug358(function):
    def wrapper(_self, *args, **kwargs):
        skip_text = 'This test is broken with PhantomJS/GhostDriver. See https://github.com/detro/ghostdriver/issues/358'
        if _self.selenium.capabilities['browserName'] == 'phantomjs':
            _self.skipTest(skip_text)
        return function(_self, *args, **kwargs)
    return wrapper

def application(environ, start_response):
    if _websocket_url and environ.get('PATH_INFO').startswith(_websocket_url):
        return _websocket_app(environ, start_response)
    return DjangoWhiteNoise(_django_app)(environ, start_response)

def login_required(username='user1', password='user1', displayed_username=None, webdriver=None):
    if displayed_username is None:
        displayed_username = username
    def login_required_decorator(function):
        def wrapper(_self, *args, **kwargs):
            _self.login(username, password, displayed_username, webdriver=webdriver)
            function(_self, *args, **kwargs)
            _self.logout(webdriver=webdriver)
        return wrapper
    return login_required_decorator


class MultiThreadLiveServerThread(LiveServerThread):
    """
    Thread for running a live multithread http server while the tests are running.
    """

    def _create_server(self, port):
        httpd_cls = type('WSGIServer', (ThreadingMixIn, WSGIServer), {'daemon_threads': True})
        return httpd_cls((self.host, port), QuietWSGIRequestHandler)


class MultiThreadLiveServerTestCase(StaticLiveServerTestCase):
    """ This class extends the StaticLiveServerTestCase with a webserver that supports
    multithreading."""

    @classmethod
    def _create_server_thread(cls, host, possible_ports, connections_override):
        return MultiThreadLiveServerThread(
            host,
            possible_ports,
            cls.static_handler,
            connections_override=connections_override,
        )


class LexpageTestCase(MultiThreadLiveServerTestCase):

    @classmethod
    def newWebDriver(cls):
        selenium = WebDriver()
        selenium.implicitly_wait(5)
        selenium.set_window_size(1280, 1024)

        print('-- Capabilities for %s --' % settings.SELENIUM_WEBDRIVER)
        capabilities = selenium.capabilities
        for key, value in capabilities.items():
            print(key, ':', value)
        print('-- End of capabilities --')
        return selenium

    @classmethod
    def setUpClass(cls):
        cls.selenium = cls.newWebDriver()

        super(LexpageTestCase, cls).setUpClass()
        cls.server_thread.httpd.set_app(application)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LexpageTestCase, cls).tearDownClass()

    def get_webdriver(self, name):
        if name is None:
            name = 'selenium'
        return getattr(self, name)

    def tearDown(self):
        directory = settings.SCREENSHOTS_DIRECTORY
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = "%s.%s.png" % (settings.SELENIUM_WEBDRIVER, self.id())
        path_to_filename = os.path.join(directory, filename)
        try:
            self.selenium.save_screenshot(path_to_filename)
        except:
            pass
        super(LexpageTestCase, self).tearDown()

    def go_to_login_form(self, webdriver=None):
        wd = self.get_webdriver(webdriver)
        wd.get('%s%s' % (self.live_server_url, reverse('auth_login')))

    def fill_in_login_form(self, username, password, webdriver=None):
        wd = self.get_webdriver(webdriver)
        wd.get('%s%s' % (self.live_server_url, reverse('auth_login')))
        username_input = wd.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = wd.find_element_by_name("password")
        password_input.send_keys(password)
        wd.find_element_by_xpath('//button[text()="S\'identifier"]').click()

    def login(self, username, password, displayed_username=None, webdriver=None):
        wd = self.get_webdriver(webdriver)
        if displayed_username is None:
            displayed_username = username
        self.go_to_login_form(webdriver=webdriver)
        self.fill_in_login_form(username, password, webdriver=webdriver)
        WebDriverWait(wd, 10).until(
            lambda driver: driver.find_element_by_xpath('//p[contains(text(),"Bienvenue %s")]' % displayed_username))

    def logout(self, webdriver=None):
        wd = self.get_webdriver(webdriver)
        lexpagiens_link = self.find_link_with_icon('Lexpagiens', webdriver=webdriver)
        ActionChains(wd).move_to_element(lexpagiens_link).perform()
        disconnect_link = self.find_link_with_icon('Se déconnecter', webdriver=webdriver)
        disconnect_link.click()
        WebDriverWait(wd, 2).until(
            lambda driver: driver.find_element_by_xpath('//p[text()=\'Vous êtes maintenant déconnecté de votre compte. \']'))

    def login_failure(self, username, password, webdriver=None):
        wd = self.get_webdriver(webdriver)
        self.go_to_login_form()
        error_message = 'Erreur lors de la validation'
        error_message_xpath = '//strong[text()="%s"]' % error_message
        with self.assertRaises(NoSuchElementException):
            wd.find_element_by_xpath(error_message_xpath)
        self.fill_in_login_form(username, password, webdriver=webdriver)
        wd.find_element_by_xpath(error_message_xpath)

    def wait_for_minichat_ready(self, webdriver=None):
        wd = self.get_webdriver(webdriver)
        disabled_input = '//p[text()[contains(.,"Connexion...")]]'
        WebDriverWait(wd, 10).until_not(
            lambda driver: driver.find_element_by_xpath(disabled_input))

    def check_notification_count(self, count, webdriver=None):
        wd = self.get_webdriver(webdriver)
        notif_xpath = '//span[@class="fa fa-bell" and contains(text(),"%s")]' % count
        WebDriverWait(wd, 5).until(
            lambda driver: driver.find_element_by_xpath(notif_xpath))

    def find_link_with_icon(self, text, webdriver=None):
        wd = self.get_webdriver(webdriver)
        xpath = '//a[text()[contains(.,"%s")]]' % (text)
        return wd.find_element_by_xpath(xpath)
