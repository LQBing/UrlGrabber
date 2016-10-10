# coding:utf-8
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin, urlunparse

DEBUG = True

if DEBUG is True:
    SKIP_INFO = False


def skip_info(info_string):
    if SKIP_INFO:
        print(info_string)


class GrabJob:
    # key is url. value False means the url is been grabbed, True means not.
    grabbed_list = list()
    grab_list = list()
    grab_out_site = False
    grab_domain = list()

    exclude_suffix_list = ['.jpg', '.jpeg', '.gif', '.bmp', '.png', '.mp3', '.mp4', '.rm', '.rmvb', '.wmv', '.mkv',
                           '.wav', '.swf', '.mpeg']
    skip_url_list = []

    def __need_add_to_grab_list__(self, grab_url):
        grab_url = grab_url.strip()
        url_parse = urlparse(grab_url)
        # skip js link
        if 'javascript:' == grab_url[:11]:
            skip_info('skip js link')
            return False
        # skip mail to link
        if 'mailto:' == grab_url[:7]:
            skip_info('skip mail link')
            return False
        # skip movie file, pic file .etc link
        if self.exclude_suffix_list:
            for exclude_item in self.exclude_suffix_list:
                if grab_url[-len(exclude_item):] == exclude_item:
                    skip_info('skip exclude file url %s')
                    return False
        # skip not allow domain url
        if url_parse.netloc not in self.grab_domain:
            skip_info('skip not allow domain url %s' % grab_url)
            return False
        # skip grabbed url
        if grab_url in self.skip_url_list:
            skip_info('skip  %s' % grab_url)
            return False
        # skip grabbed url
        if grab_url in self.grabbed_list:
            skip_info('skip grabbed url %s' % grab_url)
            return False
        # skip grab urls
        if grab_url in self.grab_list:
            skip_info('skip in list url %s' % grab_url)
            return False
        return True

    def __grab__(self, grab_url):
        grab_url = str.strip(grab_url)
        grab_url_parse = urlparse(grab_url)
        grab_domain = grab_url_parse.scheme + '://' + grab_url_parse.netloc
        if grab_url in self.grabbed_list:
            raise ValueError('%s has been grabbed' % grab_url)
        else:
            r = requests.get(url=grab_url)
            soup = BeautifulSoup(r.text, "html.parser")
            print('grab %s' % grab_url)
            # print(soup.findAll("a"))
            for item in soup.findAll("a"):
                href = item.get('href').strip()
                # deal no domain url
                href = urljoin(grab_domain, href)
                if href:
                    # deal href with domain
                    if self.__need_add_to_grab_list__(href):
                        print('+ add url %s' % href)
                        self.grab_list.append(href)
            self.grab_list.remove(grab_url)
            self.grabbed_list.append(grab_url)

    def grab(self, grab_url):
        self.grab_list.append(grab_url)
        # get domain
        url_parse = urlparse(grab_url)
        self.grab_domain.append(url_parse.netloc)
        while self.grab_list:
            self.__grab__(self.grab_list[0])
