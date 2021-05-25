#!/usr/bin/env python3

import warnings, itertools
from Wappalyzer import Wappalyzer, WebPage
from pyppeteer import launch
from pyppeteer.errors import PageError, TimeoutError
import asyncio, sys, json, os
from functools import reduce
import click



class WebDetect:
    def __init__(self):
        warnings.filterwarnings("ignore", message="""Caught 'unbalanced parenthesis at position 119' compiling regex""", category=UserWarning )
        self.requests = []
        self.pages = []
        self.responses = []
        self.technologies = []
        self.wappalyzer = Wappalyzer.latest()
        self.analyzeComplete = False
        self.tasks_status = [False]
        self.browser = None
        self.logging = False

    def requestsCatch(self, event):
        self.requests.append(event['documentURL'])


    async def openPages(self, browser, tabs):
        allpages = await browser.pages()
        if(tabs < len(allpages)):
            [await page.close() for page in allpages[tabs:]]
        else:
            [asyncio.ensure_future(browser.newPage()) for tab in range(tabs - len(await browser.pages()))]

    async def loadPage(self, page, domain, key):
        self.analyzeComplete = False
        requests = set()

        client = await page.target.createCDPSession()
        await client.send('Network.enable')
        client.on('Network.requestWillBeSent', lambda event: requests.add(event['documentURL']))
        try:
            response = await page.goto(domain, {"waitUntil": ["domcontentloaded"]})
        except TimeoutError:
            try:
                response = await page.reload({ "waitUntil": ["domcontentloaded"] });
            except:
                response = ""
        except PageError:
            response = ""

        self.responses.append({
            "domain": domain,
            "page": page,
            "response": response,
            "requests": requests,
        })

        await self.analyzePage(key)

    async def loadPages(self, pages):
        self.pages = await self.browser.pages()
        while(len(self.pages) != len(pages)):
            await asyncio.sleep(1)
            self.pages = await self.browser.pages()

        return [asyncio.ensure_future(self.loadPage(self.pages[index], domain, index)) for (index, domain) in enumerate(pages)]

    async def analyzePage(self, responseKey):
        response = self.responses.pop()
        page = response['page']
        headers = response['response'].headers if response['response'] else {}
        domain = response['domain']
        requests = list(response['requests'])

        webpage = WebPage(page.url, await page.content(), headers)
        detectedData = {
            "domain": domain,
            "technologies": dict(self.wappalyzer.analyze_with_versions_and_categories(webpage)),
            "requests": requests
        }
        self.technologies.append(detectedData)
        asyncio.ensure_future(self.log(detectedData))
        self.tasks_status[responseKey] = True

    async def detect(self, domainList, maxtabs=5, headless=True, logging=False):
        maxtabs = int(maxtabs)
        self.logging = logging
        domains = enumerate(domainList)
        try:
            while True:
                currentDomains = itertools.islice(domains, maxtabs)
                domainsToLoad = [self.validateUrl(domain.rstrip("\n")) for (index, domain) in currentDomains]
                if(len(domainsToLoad)):
                    if(self.browser == None):
                        self.browser = await launch({ "args": ['--no-sandbox', '--disable-dev-shm-usage'], "headless": headless})
                    await self.openPages(self.browser, len(domainsToLoad))
                    self.tasks_status = [False] * len(domainsToLoad)

                    await self.loadPages(domainsToLoad)
                    while True:
                        await asyncio.sleep(0.5)
                        if reduce(lambda x, y: x and y, self.tasks_status):
                            break
                else:
                    break

            await self.browser.close()
            return self.technologies
        except KeyboardInterrupt:
            return False

    async def log(self, data):
        if(self.logging):
            print(data)

    def validateUrl(self, url):
        url = str(url)
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url
        return url

async def main(domains, tabs, headless, format):
    result = await WebDetect().detect(domains, maxtabs=tabs, headless=headless, logging=(not format))
    if(format): print(json.dumps(result, indent=2))


@click.command()
@click.argument('urls', default="")
@click.option('--file', default=sys.stdin, type=click.File('r'))
@click.option('--json/--active-data', default=False, help='Print result in JSON format.')
@click.option('--tabs', default=20, help='Maximum tabs to open in chromium.')
@click.option('--headless/--no-headless', default=True, help='Whether to open chromium in headless mode.')
def detect(urls, file, json, tabs, headless):
    """webdetect v0.0.1 by @0xcrypto <vi@hackberry.xyz>"""
    if(urls or file):
        asyncio.run(main(urls if urls else file, tabs, headless, bool(json)))
    

if __name__ == '__main__':
    detect()
