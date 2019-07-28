''' memescraper '''
import os, sys
import uuid
import argparse
import logging
from urllib.parse import urlparse

import requests
import praw

class MemeScraper(object):

    # Subreddits to crawl
    SUBREDDITS = [
        'adviceanimals'
    ]

    # Mount point of photo frame
    COPY_PATH = '/Volumes/MEMORY/'

    def __init__(self, user=None, passwd=None,
            copy_path=None, sections=None, loglevel='ERROR'):
        ''' Setup or MemeScraper '''
        self.reddit_inst = praw.Reddit(user_agent='memescraper')
        if user and passwd:
            self.reddit_inst.login(user, passwd)

        self.copy_path = copy_path or self.COPY_PATH
        self.src_reddits = sections or self.SUBREDDITS
        self.image_links = []

        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=numeric_level)

    def _imgur_translate(self, link):
        ''' Takes imgur links and converts them to the direct image link '''
        parsed_url = urlparse(link.rstrip('/'))
        image_key = parsed_url.path.split('/')[-1]
        return 'http://i.imgur.com/%s.jpg' % image_key

    def _qkme_translate(self, link):
        ''' Takes qkme links and converts them to the direct image '''
        parsed_url = urlparse(link.rstrip('/'))
        image_key = parsed_url.path.split('/')[-1]
        return 'http://i.qkme.me/%s.jpg' % image_key

    def get_direct_img_link(self, link):
        ''' Takes links, and tries to get the actual image urls '''
        if link.endswith('.jpg') or link.endswith('.png'):
            # Already have a direct link, pass it
            logging.debug('%s links directly to an image', link)
            self.image_links.append(link)

        elif 'qkme' in link or 'quickmeme' in link:
            # Translate QuickMeme links
            logging.debug('%s is a quickmeme link', link)
            self.image_links.append(self._qkme_translate(link))

        elif 'imgur' in link:
            # Translate imagur links
            logging.debug('%s is an imgur link', link)
            self.image_links.append(self._imgur_translate(link))

        else:
            logging.warn('Unable to translate %s', link)

    def _store_photos(self):
        ''' Take the links, get the photos, store them, and remove old ones '''
        logging.info('Storing photos')
        if not os.path.exists(self.copy_path):
            logging.error("%s does not exist.", self.copy_path)
            return

        for img in os.listdir(self.copy_path):
            # Remove the old photos
            if img.endswith('.jpg') or img.endswith('.png'):
                os.remove(os.path.join(self.copy_path, img))

        # Retrieve and store photos
        new_photo_count = 0
        for link in self.image_links:
            resp = requests.get(link)
            if resp.status_code != 200:
                logging.error("%s returned a status code of %s",
                    link, resp.status_code)
                continue

            if link.endswith('.png'):
                file_name = '%s.png' % os.path.join(
                    self.copy_path, str(uuid.uuid4()))
            else:
                file_name = '%s.jpg' % os.path.join(
                    self.copy_path, str(uuid.uuid4()))

            img = open(file_name, 'wb')
            img.write(resp.content)
            img.close()
            new_photo_count += 1

        print ('Stored %s new photos' % new_photo_count)

    def process(self):
        ''' Process our meme links '''
        logging.info('Starting subreddit processing')
        for subreddit in self.src_reddits:
            logging.info('Processing %s', subreddit)
            top_posts = self.reddit_inst.get_subreddit(subreddit).get_top(
                limit=100)
            hot_posts = self.reddit_inst.get_subreddit(subreddit).get_top(
                limit=100)
            all_posts = list(hot_posts) + list(top_posts)
            for post in all_posts:
                if not post.over_18:
                    self.get_direct_img_link(post.url)
        # Nuke any dupes we picked up
        self.image_links = set(self.image_links)
        self._store_photos()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape some memes!')
    parser.add_argument('-u', '--user', help='Reddit username')
    parser.add_argument('-p', '--passwd', help='Reddit password')
    parser.add_argument('-c', '--path', help='Path to copy images to')
    parser.add_argument(
        '-s',
        '--subreddits',
        help='Subreddits to crawl',
        nargs='+')
    parser.add_argument('-l', '--loglevel',
        help='Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL',
        default='WARN')
    args = parser.parse_args()
    scraper = MemeScraper(
        user=args.user,
        passwd=args.passwd,
        copy_path=args.path,
        sections=args.subreddits,
        loglevel=args.loglevel.upper())
    sys.exit(scraper.process())