#!/usr/bin/python2.7
# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Terms of Services page."""

__author__ = 'ichikawa@google.com (Hiroshi Ichikawa)'

import logging
import traceback
import urllib2
import urlparse

import lxml.etree

import utils


class Handler(utils.BaseHandler):

    repo_required = False

    def get(self):
        article_html = None

        # Fetches the ToS page and embed it in the page. We do this instead of
        # just redirecting to the ToS page because we need to host the content
        # in our domain in zero-rating mode. See "Zero-rating" section of the
        # admin page (app/resources/admin.html.template) for details of
        # zero-rating mode.
        try:
            if self.config.tos_url:
                res = urllib2.urlopen(self.config.tos_url)
                tos_html = res.read()
                doc = lxml.etree.HTML(tos_html)
                articles = doc.xpath("//div[@class='maia-article']")
                if articles:
                    article = articles[0]
                    for anchor in article.xpath('.//a'):
                        href = anchor.attrib.get('href')
                        if href and anchor.text:
                            # Converts relative URLs to absolute URLs.
                            anchor.attrib['href'] = urlparse.urljoin(
                                    res.geturl(), href)
                            anchor.text += ' (external site)'
                    article_html = lxml.etree.tostring(article, method='html')

        except:
            logging.error(
                'Error during fetching/parsing the ToS page from %s\n%s',
                self.config.tos_url,
                traceback.format_exc())

        self.render(
                'tos.html',
                article_html=article_html,
                tos_url=self.config.tos_url)
