import time as t
from datetime import datetime, date, time
import requests
from bs4 import BeautifulSoup as bs

class ProxyManager:
    def __init__(self):
        self.proxies = self.__get_proxies().copy()
        self.current = ''
        self.used = []
        self.counter = 0
        self.l = len(self.proxies)

    def __get_proxies(self):
        with open('proxy-list.txt', 'r', encoding='utf8') as file:
            proxs = file.read().strip().split('\n')
        return proxs

    def get_current(self):
        self.current = self.proxies[self.counter]
        proxy = self.current
        return {"http": f'http://{proxy}', "https": f'http://{proxy}'}

    def next(self):
        self.counter += 1
        self.used.append(self.current)
        if self.counter < self.l:
            next_proxy = self.proxies[self.counter]
            self.current = next_proxy
        else:
            self.proxies = self.used.copy()
            self.used.clear()
            self.counter = 0
    