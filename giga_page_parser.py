#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from HTMLParser import HTMLParser
import sys
import logging
import os.path
import re

class GigaProduct:
    def __init__(self):
        self.id = 0
        self.code = u''
        self.title = u''
        self.large_pic_href = u''
        self.small_pic_href = u''
        self.actresses = []
        self.tags = []

    def set_product(self, id, code, title, large_pic_href, small_pic_href):
        self.id = id
        self.code = code
        self.title = title
        self.large_pic_href = large_pic_href
        self.small_pic_href = small_pic_href

    def get_actress_string(self):
        actress_str = ''
        for actress in self.actresses:
            actress_str = '%s,%s' % (actress_str, actress[1])
        actress_str = actress_str[1:]
        return actress_str

class GigaPageParser(HTMLParser):
    STATE_INIT = 0
    STATE_WORKS_PIC = 10
    STATE_WORKS_TXT = 20
    STATE_WORKS_TXT_CODE = 21
    STATE_WORKS_TXT_CODE_DD = 22
    STATE_WORKS_TXT_ACTRESS = 23
    STATE_WORKS_TXT_ACTRESS_A = 24
    STATE_ID_NUMBER = 30
    STATE_ID_NUMBER_DD = 40
    STATE_DIV_TAG = 50
    STATE_DIV_TAG_A = 51

    def init(self, file):
        self.code = u''
        self.id = int(os.path.basename(file).replace('.html', ''))
        self.title = u''
        self.large_pic_href = u''
        self.small_pic_href = u''
        self.tags = []
        self.actress = []
        self.state = GigaPageParser.STATE_INIT

    @classmethod
    def state_name(GigaPageParser, state):
        if state == GigaPageParser.STATE_INIT:
            return 'STATE_INIT'
        elif state == GigaPageParser.STATE_WORKS_PIC:
            return 'STATE_WORKS_PIC'
        elif state == GigaPageParser.STATE_WORKS_TXT:
            return 'STATE_WORKS_TXT'
        elif state == GigaPageParser.STATE_WORKS_TXT_CODE:
            return 'STATE_WORKS_TXT_CODE'
        elif state == GigaPageParser.STATE_WORKS_TXT_CODE_DD:
            return 'STATE_WORKS_TXT_CODE_DD'
        elif state == GigaPageParser.STATE_WORKS_TXT_ACTRESS:
            return 'STATE_WORKS_TXT_ACTRESS'
        elif state == GigaPageParser.STATE_WORKS_TXT_ACTRESS_A:
            return 'STATE_WORKS_TXT_ACTRESS_A'
        elif state == GigaPageParser.STATE_ID_NUMBER:
            return 'STATE_ID_NUMBER'
        elif state == GigaPageParser.STATE_ID_NUMBER_DD:
            return 'STATE_ID_NUMBER_DD'
        elif state == GigaPageParser.STATE_DIV_TAG:
            return 'STATE_DIV_TAG'
        elif state == GigaPageParser.STATE_DIV_TAG_A:
            return 'STATE_DIV_TAG_A'
        else:
            return 'STATE_UNKNOWN'

    def transist_state(self, state):
        old_state = self.state
        logging.debug('Transists state from %s to %s', GigaPageParser.state_name(old_state), GigaPageParser.state_name(state))
        self.state = state

    def handle_starttag(self, tag, attrs):
        logging.debug('handle_starttag: %s %s' % (tag, attrs))
        if self.state == GigaPageParser.STATE_INIT:
            if tag == 'div' and len(attrs) > 0 and attrs[0][0] == 'id':
                if attrs[0][1] == 'works_pic':
                    logging.debug('find works_pic')
                    self.transist_state(GigaPageParser.STATE_WORKS_PIC)
                elif attrs[0][1] == 'works_txt':
                    logging.debug('find works_txt')
                    self.transist_state(GigaPageParser.STATE_WORKS_TXT)
                elif attrs[0][1] == 'tag_main':
                    logging.debug('find tag_main')
                    self.transist_state(GigaPageParser.STATE_DIV_TAG)

        elif self.state == GigaPageParser.STATE_WORKS_PIC:
            if tag == 'a' and len(attrs) >= 3:
                if attrs[0][0] == 'href':
                    logging.debug('find large_pic_href')
#                    self.large_pic_href = unicode(attrs[0][1], 'utf-8')
                    self.large_pic_href = attrs[0][1]
                if attrs[2][0] == 'title':
                    logging.debug('find title')
#                    self.title = unicode(attrs[2][1], 'utf-8')
                    self.title = attrs[2][1]

            elif tag == 'img' and len(attrs) >= 3:
                if attrs[0][0] == 'src':
                    logging.debug('find small_pic_href')
#                    self.small_pic_href = unicode(attrs[0][1], 'utf-8')
                    self.small_pic_href = attrs[0][1]
                self.transist_state(GigaPageParser.STATE_INIT)

        elif self.state == GigaPageParser.STATE_WORKS_TXT_CODE:
            if tag == 'dd':
                self.transist_state(GigaPageParser.STATE_WORKS_TXT_CODE_DD)

        elif self.state == GigaPageParser.STATE_WORKS_TXT_CODE_DD:
            pass

        elif self.state == GigaPageParser.STATE_WORKS_TXT_ACTRESS:
            if tag == 'a' and len(attrs) >= 1:
                if attrs[0][0] == 'href':
                    logging.debug('find flag_actress_href')
                    match_result = re.search('(?<=actor_id=)[0-9]+', attrs[0][1])
                    if match_result:
                        self.transist_state(GigaPageParser.STATE_WORKS_TXT_ACTRESS_A)
                        self.actor_id = int(match_result.group(0))

        elif self.state == GigaPageParser.STATE_WORKS_TXT_ACTRESS_A:
            pass

        elif self.state == GigaPageParser.STATE_ID_NUMBER:
            if tag == 'dd':
                logging.debug('flag_codenumber+dd')
                self.transist_state(GigaPageParser.STATE_ID_NUMBER_DD)

        elif self.state == GigaPageParser.STATE_ID_NUMBER_DD:
            pass

        elif self.state == GigaPageParser.STATE_DIV_TAG:
            if tag == 'a' and len(attrs) >= 1:
                if attrs[0][0] == 'href':
                    logging.debug('find flag_tag_href')
                    match_result = re.search('(?<=tag_id=)[0-9]+', attrs[0][1])
                    if match_result:
                        self.transist_state(GigaPageParser.STATE_DIV_TAG_A)
                        self.tag_id = int(match_result.group(0))
 
    def handle_endtag(self, tag):
        logging.debug('handle_endtag: %s', tag)
        if self.state == GigaPageParser.STATE_INIT:
            pass
        elif self.state == GigaPageParser.STATE_WORKS_PIC:
            pass    
        elif self.state == GigaPageParser.STATE_WORKS_TXT:
            if tag == 'div':
                self.transist_state(GigaPageParser.STATE_INIT)
        elif self.state == GigaPageParser.STATE_WORKS_TXT_CODE:
            pass
        elif self.state == GigaPageParser.STATE_WORKS_TXT_CODE_DD:
            pass
        elif self.state == GigaPageParser.STATE_WORKS_TXT_ACTRESS:
            if tag == 'span':
                self.transist_state(GigaPageParser.STATE_WORKS_TXT)
        elif self.state == GigaPageParser.STATE_WORKS_TXT_ACTRESS_A:
            if tag == 'a':
                self.transist_state(GigaPageParser.STATE_WORKS_TXT_ACTRESS)
                
        elif self.state == GigaPageParser.STATE_ID_NUMBER:
            pass
        elif self.state == GigaPageParser.STATE_ID_NUMBER_DD:
            pass
        elif self.state == GigaPageParser.STATE_DIV_TAG:
            if tag == 'div':
                self.transist_state(GigaPageParser.STATE_INIT)
                self.tag_id = 0
        elif self.state == GigaPageParser.STATE_DIV_TAG_A:
            if tag == 'a':
                self.transist_state(GigaPageParser.STATE_DIV_TAG)

    def handle_data(self, data):
        logging.debug('handle_data: %s', data)

        str = data
        if self.state == GigaPageParser.STATE_INIT:
            pass
        elif self.state == GigaPageParser.STATE_WORKS_PIC:
            pass    
        elif self.state == GigaPageParser.STATE_WORKS_TXT:
            if str == u'\u4f5c\u54c1\u756a\u53f7':
                self.transist_state(GigaPageParser.STATE_WORKS_TXT_CODE)
            elif str == u'\u51fa\u6f14\u5973\u512a':
                self.transist_state(GigaPageParser.STATE_WORKS_TXT_ACTRESS)
                
        elif self.state == GigaPageParser.STATE_WORKS_TXT_CODE:
            pass
        elif self.state == GigaPageParser.STATE_WORKS_TXT_CODE_DD:
            self.code = str
            self.transist_state(GigaPageParser.STATE_WORKS_TXT)

        elif self.state == GigaPageParser.STATE_WORKS_TXT_ACTRESS:
            pass
        elif self.state == GigaPageParser.STATE_WORKS_TXT_ACTRESS_A:
            self.actress.append((self.actor_id, str))

        elif self.state == GigaPageParser.STATE_ID_NUMBER:
            pass
        elif self.state == GigaPageParser.STATE_ID_NUMBER_DD:
            pass

        elif self.state == GigaPageParser.STATE_DIV_TAG:
            pass
        elif self.state == GigaPageParser.STATE_DIV_TAG_A:
            self.tags.append((self.tag_id, str))

    def parse_content(self, file):
        logging.info("Parsing page: %s", file)
        self.init(file)
        fp = open(file, mode='r')
        content = fp.read()
        u_content = unicode(content, 'utf-8')
        self.feed(u_content)
        self.close()
        if self.code and self.title:
            product = GigaProduct()
            product.set_product(self.id, self.code, self.title, self.large_pic_href, self.small_pic_href)
            product.actresses = self.actress
            product.tags = self.tags
            return product
        else:
            logging.error('Failed to parse page : %s', file)
        return None

if __name__ == '__main__':
    if not sys.argv:
        sys.exit('')
    parser = GigaPageParser()
    if parser.parse_content(sys.argv[1]):
        print("Id=%d" % parser.id)
        print("Code=%s" % parser.code)
        print("Title=%s" % parser.title)
        print("Actress=", parser.actress)
        print("Tags=", parser.tags)
        print("Large Picture=%s" % parser.large_pic_href)
        print("Small Picture=%s" % parser.small_pic_href)
