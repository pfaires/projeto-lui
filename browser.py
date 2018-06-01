# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import http.cookiejar


class Browser(object):
    """ Um navegador para a captura de paginas da internet """

    # armazenamento para os cookies de navegação
    cookies = http.cookiejar.CookieJar()

    # o user agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"

    def __init__(self):
        # configuração do urllib2
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookies)
        )
        opener.addheaders = [('User-agent', self.user_agent),
                             ('Accept-encoding', 'utf-8')]
        self.opener = opener

    def get(self, url):
        """ Recupera uma URL http usando o método GET """
        return self.opener.open(url)
    
    def post(self, url, data):
        """ Recupera uma URL http usando o método POST """
        return self.opener.open(url, urllib.parse.urlencode(data).encode("ascii"))

    def clear(self):
        """ Limpa os cookies do browser """
        self.cookies.clear()
