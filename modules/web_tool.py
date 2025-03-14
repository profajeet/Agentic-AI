# !pip install googlesearch-python
import re
from googlesearch import search
import requests
from bs4 import BeautifulSoup

class web_tool:
    def __init__(self,max_result=2):
        self.max_result =max_result

    def validate_url(self,url: str) -> bool:
        """Validate the url.
        Args:
            url: The website url.
        """
        # Regular expression for validating a URL
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, url) is not None:
            return True
        else:
            return False
        
    def web_scrape(self, url: str) -> str:
        """Scrape the website for the url.

        Args:
            url: The website url.
        """
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html5lib') # html5lib parser is used to parse the content
        # soup = BeautifulSoup(page.text, 'html.parser')
        # print(soup.prettify())
        return soup.get_text()
        
    def invoke(self,topic):
        """
        Search, process and return the url and content list of dictionaries.
        Args:
            topic: search topic
        """
        results = search(topic, advanced=True)
        urls= [url.url for url in results if self.validate_url(url.url)][:self.max_result]
        final_list = []
        for url in urls:
            content = self.web_scrape(url) 
            # implement text preprocessing to filter the content.
            final_list.append({'url':url,'content':content})
        return final_list