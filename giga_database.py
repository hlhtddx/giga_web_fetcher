#!/usr/bin/env python
# -*- coding: utf-8 -*-

from giga_page_parser import GigaPageParser
import sqlite3
import sys
import logging

class GigaDatabase:
    def __init__(self, dbname):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def drop_table(self):
        sqls = [
                'DROP TABLE IF EXISTS `map_product_tag`',
                'DROP TABLE IF EXISTS `map_product_actress`',
                'DROP TABLE IF EXISTS `actress`',
                'DROP TABLE IF EXISTS `tag`',
                'DROP TABLE IF EXISTS `product`'
            ]
        for sql in sqls:
            logging.info("SQL: %s", sql)
            self.conn.execute(sql)

    def open_or_create_table(self):
        sqls = [
            '''CREATE TABLE IF NOT EXISTS `product` (
                `product_id` INTEGER PRIMARY KEY,
                `code` text NOT NULL,
                `title` text NOT NULL,
                `large_pic_href` text NOT NULL,
                `small_pic_href` text NOT NULL
                ) WITHOUT ROWID''',
            '''CREATE TABLE IF NOT EXISTS `actress` (
                `actress_id` INTEGER PRIMARY KEY,
                `name` text NOT NULL
                ) WITHOUT ROWID''',
            '''CREATE TABLE IF NOT EXISTS `tag` (
                `tag_id` INTEGER PRIMARY KEY,
                `name` text NOT NULL
                ) WITHOUT ROWID''',
            '''CREATE TABLE IF NOT EXISTS `map_product_tag` (
                `product_id` INTEGER,
                `tag_id` INTEGER,
                FOREIGN KEY(product_id) REFERENCES product(product_id),
                FOREIGN KEY(tag_id) REFERENCES tag(tag_id)
                )''',
            '''CREATE TABLE IF NOT EXISTS `map_product_actress` (
                `product_id` INTEGER,
                `actress_id` INTEGER,
                FOREIGN KEY(product_id) REFERENCES product(product_id),
                FOREIGN KEY(actress_id) REFERENCES actress(actress_id)
                )'''
        ]

        for sql in sqls:
            logging.info("SQL: %s", sql)
            self.conn.execute(sql)

    def get_all_products(self):
        sql = 'SELECT * from `product`'
        cursor = self.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_all_actresses(self):
        sql = 'SELECT * from `actress`'
        cursor = self.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_all_tags(self):
        sql = 'SELECT * from `tag`'
        cursor = self.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_all_actresses_of_product(self):
        sql = 'SELECT * from `map_product_actress`'
        cursor = self.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_all_tags_of_product(self):
        sql = 'SELECT * from `map_product_tag`'
        cursor = self.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return rows

class GigaProduct:
    def __init__(self, id, code, title, large_pic_href, small_pic_href):
        self.id = id
        self.code = code
        self.title = title
        self.large_pic_href = large_pic_href
        self.small_pic_href = small_pic_href
        self.actresses = []
        self.tags = []

    def get_actress_string(self):
        actress_str = ''
        for actress in self.actresses:
            actress_str = '%s,%s' % (actress_str, actress[1])
        actress_str = actress_str[1:]
        return actress_str

class GigaProductMap:
    def __init__(self):
        self.products = {}
        self.products_code = {}
        self.tags = {}
        self.actresses = {}
        self.map_product_tag = {}
        self.map_product_actress = {}

    def parse_pages(self, pages):
        for page in pages:
            parser = GigaPageParser()

            if parser.parse_content(page):
                product = GigaProduct(parser.id, parser.code, parser.title, parser.large_pic_href, parser.small_pic_href)
                self.products[parser.id] = product
                self.products_code[parser.code] = product
                for tag in parser.tags:
                    self.tags[tag[0]] = tag
                    product.tags.append(tag)
                    self.map_product_tag[(parser.id, tag[0])] = 1
                for actress in parser.actress:
                    self.actresses[actress[0]] = actress
                    product.actresses.append(actress)
                    self.map_product_actress[(parser.id, actress[0])] = 1

    def load_from_database(self, database):
        product_list = database.get_all_products()
        tag_list = database.get_all_tags()
        actress_list = database.get_all_actresses()
        product_tag = database.get_all_tags_of_product()
        product_actress = database.get_all_actresses_of_product()

        for prod in product_list:
            product = GigaProduct(prod[0], prod[1], prod[2], prod[3], prod[4])
            self.products[product.id] = product
            self.products_code[product.code] = product

        for tag in tag_list:
            self.tags[tag[0]] = tag

        for actress in actress_list:
            self.actresses[actress[0]] = actress

        for pt_pair in product_tag:
            self.map_product_tag[pt_pair] = 1
            product = self.products[pt_pair[0]]
            tag = self.tags[pt_pair[1]]
            product.tags.append(pt_pair)

        for pa_pair in product_actress:
            self.map_product_actress[pa_pair] = 1
            product = self.products[pa_pair[0]]
            actress = self.actresses[pa_pair[1]]
            product.actresses.append(actress)

    def save_products(self, conn):
        sql = 'INSERT INTO `product` VALUES(?, ?, ?, ?, ?)'
        cursor = conn.cursor()
        pkeys = self.products.keys()
        pkeys.sort()
        for p in pkeys:
            product = self.products[p]
            cursor.execute(sql, (product.id, product.code, product.title, product.large_pic_href, product.small_pic_href))
        cursor.close()

    def save_tags(self, conn):
        sql = 'INSERT INTO `tag` VALUES(?, ?)'
        cursor = conn.cursor()
        pkeys = self.tags.keys()
        pkeys.sort()
        for p in pkeys:
            tag = self.tags[p]
            cursor.execute(sql, tag)
        cursor.close()

    def save_actresses(self, conn):
        sql = 'INSERT INTO `actress` VALUES(?, ?)'
        cursor = conn.cursor()
        pkeys = self.actresses.keys()
        pkeys.sort()
        for p in pkeys:
            actress = self.actresses[p]
            cursor.execute(sql, actress)
        cursor.close()

    def save_map(self, conn, map, map_name):
        sql = 'INSERT INTO `%s` VALUES(?, ?)' % map_name
        cursor = conn.cursor()
        pkeys = map.keys()
        pkeys.sort()
        for p in pkeys:
            logging.info("save to map:%s(id=%d, ref_id=%d", map_name, p[0], p[1])
            cursor.execute(sql, p)
        cursor.close()

    def save(self, conn):
        self.save_products(conn)
        self.save_tags(conn)
        self.save_actresses(conn)
        self.save_map(conn, self.map_product_tag, 'map_product_tag')
        self.save_map(conn, self.map_product_actress, 'map_product_actress')

    def find_product(self, code):
        if not self.products_code.has_key(code):
            return None
        product = self.products_code[code]
        return product

    def dump_products(self):
        pkeys = self.products.keys()
        pkeys.sort()
        for p in pkeys:
            product = self.products[p]
            print('(%d) %s %s %s' % (product.id, product.code, product.title, product.get_actress_string()))

    def dump_tags(self):
        pkeys = self.tags.keys()
        pkeys.sort()
        for p in pkeys:
            tag = self.tags[p]
            print('Id=%d tag_name=%s' % (tag[0], tag[1]))

    def dump_actresses(self):
        pkeys = self.actresses.keys()
        pkeys.sort()
        for p in pkeys:
            actress = self.actresses[p]
            print('Id=%d name=%s' % (actress[0], actress[1]))

    def dump(self):
        self.dump_products()
        self.dump_tags()
        self.dump_actresses()

def append_to_db(pages):
    logging.basicConfig(level=logging.WARN)
    giga = GigaProductMap()
    database = GigaDatabase('giga.db')
    giga.load_from_database(database)
    giga.parse_pages(pages)
    giga.dump()

#    giga.save(database.conn)
#    database.conn.commit()
    database.conn.close()

def init_db(pages):
    logging.basicConfig(level=logging.WARN)
    giga = GigaProductMap()
    giga.parse_pages(pages)
    giga.dump()

    database = GigaDatabase('giga.db')
    database.drop_table()
    database.open_or_create_table()
    giga.save(database.conn)
    database.conn.commit()
    database.conn.close()

def main():
    if sys.argv[1] == '--initdb':
        init_db(sys.argv[2:])
    elif sys.argv[1] == '--append':
        append_to_db(sys.argv[2:])

if __name__ == '__main__':
    main()
