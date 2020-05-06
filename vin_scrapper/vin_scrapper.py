# -*- coding: utf-8 -*-

"""Main module."""

import json
import os
import re
import subprocess
import sys
import time
from base64 import b64encode

import psutil
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ProxySettings:
    """
    Proxy contains information about proxy type and necessary proxy settings.

    Attributes:
        host (str): host
        password (str): password
        port (str): port
        username (str): username
    """

    def __init__(self, **kwargs):
        self.host = kwargs.get("host", None)
        self.port = kwargs.get("port", None)
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None)

    def __repr__(self):
        return repr(
            "<{}(host='{}', port='{}', username='{}', password='{}') at 0x{:x}>".format(
                self.__class__.__name__,
                self.host,
                self.port,
                self.username,
                self.password,
                id(self),
            )
        )


class DataStructure:
    @staticmethod
    def asdict():
        return {
            "VIN Number": "",
        }


class MissingPageSource(Exception):
    pass


class VinScrapper:
    def __init__(self, log_level="INFO", timeout=60, **kwargs):
        self.logger = logger
        self.logger.level(log_level.upper())
        self.data_structure = DataStructure.asdict()
        self._timeout = timeout
        self._closed = False
        self.proxy = None
        self._page_source = None
        self.check_kwargs(kwargs)

    def check_kwargs(self, kwargs):

        self.url = None
        self._licence_plate_webstate = None
        self._licence_plate_webinput = None
        if kwargs.get("url"):
            self.url = kwargs.get("url")
            if "vehiclehistory" in self.url:
                self._licence_plate_webinput = "input-98"
                self._licence_plate_webstate = {
                    "selector": "div.v-input--is-label-active:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1)",
                    "state": None,
                }
                self._dropdown_css_selector = ".VhSelect--light > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1)"
                self._dropdown_list_item = "list-item-231"
                self._search_button_css_selector = (
                    ".Search-licensePlate > div:nth-child(3)"
                )
                self._vin_number_class = "SummaryTopMenu-vin"

        self.licence_number = None
        if kwargs.get("licence_number"):
            self.licence_number = kwargs.get("licence_number")

        self.location = None
        if kwargs.get("location"):
            self.location = kwargs.get("location")
            if self._licence_plate_webstate:
                available_locations = {
                    "al": "alabama",
                    "ak": "alaska",
                    "az": "arizona",
                    "ar": "arkansas",
                    "ca": "california",
                    "co": "colorado",
                    "ct": "connecticut",
                    "de": "delaware",
                    "dc": "district of columbia",
                    "fl": "florida",
                    "ga": "georgia",
                    "hi": "hawaii",
                    "id": "idaho",
                    "il": "illinois",
                    "in": "indiana",
                    "ia": "iowa",
                    "ks": "kansas",
                    "ky": "kentucky",
                    "la": "louisiana",
                    "me": "maine",
                    "md": "maryland",
                    "ma": "massachusetts",
                    "mi": "michigan",
                    "mn": "minnesota",
                    "ms": "mississippi",
                    "mo": "missouri",
                    "mt": "montana",
                    "ne": "nebraska",
                    "nv": "nevada",
                    "nh": "new hampshire",
                    "nj": "new jersey",
                    "nm": "new mexico",
                    "ny": "new york",
                    "nc": "north carolina",
                    "nd": "north dakota",
                    "oh": "ohio",
                    "ok": "oklahoma",
                    "or": "oregon",
                    "pa": "pennsylvania",
                    "ri": "rhode island",
                    "sc": "south carolina",
                    "sd": "south dakota",
                    "tn": "tennessee",
                    "tx": "texas",
                    "ut": "utah",
                    "vt": "vermont",
                    "va": "virginia",
                    "wa": "washington",
                    "wv": "west virginia",
                    "wi": "wisconsin",
                    "wy": "wyoming",
                }
                try:
                    self._licence_plate_webstate["state"] = available_locations[
                        self.location.lower()
                    ]
                except KeyError:
                    raise RuntimeError(
                        f"{self.location} cannot be found in the available "
                        f"locations: {available}"
                    )

        self.headless = None
        if kwargs.get("headless"):
            self.headless = kwargs.get("headless")

        self.no_json = None
        if kwargs.get("no_json"):
            self.no_json = kwargs.get("no_json")

        self.proxy = None
        if kwargs.get("host"):
            self.proxy = ProxySettings(**kwargs)

        self.port = None
        if kwargs.get("port"):
            self.port = kwargs.get("port")

        self.username = None
        if kwargs.get("username"):
            self.username = kwargs.get("username")

        self.password = None
        if kwargs.get("password"):
            self.password = kwargs.get("password")

        self.web_username = None
        if kwargs.get("web_username"):
            self.web_username = kwargs.get("web_username")

        self.web_password = None
        if kwargs.get("web_password"):
            self.web_password = kwargs.get("web_password")

    def _setup_proxy(self):
        """Simplified Firefox Proxy settings"""
        firefox_profile = webdriver.FirefoxProfile()
        # Direct = 0, Manual = 1, PAC = 2, AUTODETECT = 4, SYSTEM = 5
        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("signon.autologin.proxy", True)
        firefox_profile.set_preference("network.websocket.enabled", False)
        firefox_profile.set_preference("network.proxy.http", self.proxy.host)
        firefox_profile.set_preference("network.proxy.http_port", int(self.proxy.port))
        firefox_profile.set_preference("network.proxy.ssl", self.proxy.host)
        firefox_profile.set_preference("network.proxy.ssl_port", int(self.proxy.port))
        # firefox_profile.set_preference("network.automatic-ntlm-auth.allow-proxies", False)
        # firefox_profile.set_preference("network.negotiate-auth.allow-proxies", False)
        firefox_profile.set_preference(
            "network.proxy.no_proxies_on", "localhost, 127.0.0.1"
        )
        # Disable images for website to load quicker
        firefox_profile.set_preference("permissions.default.image", 2)
        # Disable Flash for website to load quicker
        firefox_profile.set_preference(
            "dom.ipc.plugins.enabled.libflashplayer.so", "false"
        )
        if self.proxy.username and self.proxy.password:
            firefox_profile.set_preference(
                "network.proxy.socks_username", self.proxy.username
            )
            firefox_profile.set_preference(
                "network.proxy.socks_password", self.proxy.password
            )
        # Deprecated
        # firefox_profile.add_extension('close_proxy_authentication-1.1.xpi')
        # credentials = f"{self.proxy.username}:{self.proxy.password}"
        # credentials = b64encode(credentials.encode("ascii")).decode("utf-8")
        # firefox_profile.set_preference("extensions.closeproxyauth.authtoken", credentials)
        firefox_profile.update_preferences()
        return firefox_profile

    def open_site(self, headless=False):
        """Simple selenium webdriver to open a known url"""
        options = Options()
        options.headless = headless
        profile = None
        if self.proxy:
            self.logger.info("Accessing URL using proxy settings: {}", self.proxy)
            profile = self._setup_proxy()

        self.driver = webdriver.Firefox(
            options=options, firefox_profile=profile, timeout=self._timeout
        )
        url = "https://driving-tests.org/vin-decoder/" if not self.url else self.url
        self.logger.info("Accessing: {}", url)
        self.driver.get(url)
        self.logger.info("Successfully opened: {}", url)

    def login(self):
        if (self.web_password and self.web_username) is None:
            return
        else:
            # TODO:
            pass

    def navigate_site(self):
        """Navigate through the website"""
        licence_plate_input = WebDriverWait(self.driver, self._timeout).until(
            EC.presence_of_element_located((By.ID, self._licence_plate_webinput))
        )
        licence_plate_input = self.driver.find_element_by_id(
            self._licence_plate_webinput
        )
        licence_plate_input.send_keys(self.licence_number)
        time.sleep(1)  # Wait a second before hitting the Enter
        # Press Enter key

        dropdown_selector = self.driver.find_element_by_css_selector(
            self._dropdown_css_selector
        )
        dropdown_selector.click()
        time.sleep(1)  # Wait a second before hitting the Enter
        if dropdown_selector.is_displayed():
            time.sleep(1)  # Wait a second before hitting the Enter
            dropdown_menu_table = "#list-104"
            dropdown_menu = self.driver.find_element_by_css_selector(
                dropdown_menu_table
            )
            for i in range(4):
                time.sleep(0.5)
                dropdown_menu.send_keys(Keys.END)
            dropdown_menu.send_keys(Keys.HOME)

            locations_dict = {
                location.lower(): f"{self._dropdown_list_item}-{count}"
                for count, location in enumerate(dropdown_menu.text.split("\n"))
            }
            selected_location = locations_dict[self.location.lower()]
            location_selector = self.driver.find_element_by_id(selected_location)
            location_selector.click()
            time.sleep(0.5)  # Wait a second before hitting the Enter

            search_button = self.driver.find_element_by_css_selector(
                self._search_button_css_selector
            )
            search_button.click()
            time.sleep(1)

    @property
    def page_source(self):
        """Get page source as object"""
        self._page_source = BeautifulSoup(self.driver.page_source, "html.parser")
        return self._page_source

    def get_vehicle_details(self):
        """Get vehicle details.

        Raises:
            MissingPageSource: If missing page source, raises error and closes browser
        """

        vin_number = WebDriverWait(self.driver, self._timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, self._vin_number_class))
        )
        self.data_structure["VIN Number"] = vin_number.text.split()[-1]

    @property
    def data_as_json(self):
        """Output in the form of json file"""
        data = (
            str(self.data_structure)
            if isinstance(self.data_structure, dict)
            else self.data_structure
        )
        return json.dumps(data, sort_keys=True)

    def data_json_to_file(self, filename="data_structure.json"):
        """Save data structure as json file

        Args:
            filename (str, optional): Filename to save as.
        """
        self.logger.info("Writing data to json")
        data = (
            str(self.data_structure)
            if isinstance(self.data_structure, dict)
            else self.data_structure
        )
        with open(filename, "w") as json_file:
            json.dump(data, json_file)

    def close_session(self):
        """Close browser and cleanup"""
        if not self._closed:
            self.logger.info("Closing the browser...")
            self.driver.close()
            self.driver.quit()
            time.sleep(1)

            PROCNAME = "geckodriver"
            self.logger.info("Cleaning up by killing {} process", PROCNAME)
            _ = [
                proc.terminate()
                for proc in psutil.process_iter()
                if proc.name() == PROCNAME
            ]
            self._closed = True
            self.logger.info("Done...")
