#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = 'Niels Cautaerts'
SITENAME = 'Niels Cautaerts'
# a workaround so that the static page is first, then comes blog
# see https://stackoverflow.com/questions/23709113/in-pelican-how-to-create-a-page-dedicated-to-hosting-all-the-blog-articles
SITEURL = ''
OUTPUT_PATH = 'output/'
INDEX_SAVE_AS = 'blog_archive.html'

# custom settings
DISPLAY_CATEGORIES_ON_MENU=False
DISPLAY_PAGES_ON_MENU=False

MENUITEMS = (("Home", "/"),
             ("Blog", "/blog_archive.html"),
             #("Projects", "/projects.html"),
             ("Resume", "/cv.html"),
             ("Contact", "/contact.html"),
             )

PATH = 'content'

TIMEZONE = 'Europe/Brussels'

DEFAULT_LANG = 'en'

LOCALE = "en_US"

DEFAULT_DATE_FORMAT = '%Y-%m-%d'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = ()

# Social widget
SOCIAL = (('LinkedIn', 'https://www.linkedin.com/in/niels-cautaerts-a8a71142/'),
          ('Github', 'https://github.com/din14970'),
          ('Youtube', 'https://www.youtube.com/channel/UCc4At260tju-LVzKCuxZZVg?view_as=subscriber'),
          ('Researchgate', 'https://www.researchgate.net/profile/Niels_Cautaerts'),
          ('Google Scholar', 'https://scholar.google.be/citations?user=b0dHQdsAAAAJ&hl=en'),
          )

DEFAULT_PAGINATION = 5

# Theme
THEME = "./layout-theme"

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

