#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import logging
from giga_database import GigaProductMap, GigaProduct, GigaDatabase

def get_file_info(path, product_map):
    abspath = os.path.abspath(path.strip())
    dir = os.path.dirname(abspath)
    base = os.path.basename(abspath)
    name_parts = base.rsplit('.', 1)
    if len(name_parts) < 2:
        logging.warn('%s has not extensionm just skip it', path)
        return

    base_name = name_parts[0]
    ext_name = name_parts[1]

    pattern1 = re.compile('([a-zA-Z]+)[-_]?([0-9]+)([-_]+([0-9]+))?(.*)')
    match = pattern1.match(base_name)
    if not match:
        print('basename=%s, no matched pattern' % abspath)
        return

    print('basename=%s, code=%s, number=%s, sequence=%s, other=%s' %
        (base_name, match.group(1), match.group(2), match.group(4), match.group(5)))
    code = match.group(1).upper()
    number = int(match.group(2))
    product = None

    if number < 100:
        code_number = '%s-%02d' % (code, number)
        product = product_map.find_product(code_number)
    if not product:
        code_number = '%s-%03d' % (code, number)
        product = product_map.find_product(code_number)

    info_str = ''
    if product:
        if product.get_actress_string():
            info_str = ' (%s) %s' % (product.get_actress_string(), product.title)
        else:
            info_str = ' %s' % product.title
    else:
        logging.error('The product %s is not founded', code_number)

    seq_str = '01'
    if match.group(4):
        seq_str = match.group(4)

    new_base_name = ('%s_%s%s.%s' % (code_number, seq_str, info_str, ext_name)).replace('/', '|')

    old_path = path
    new_path = os.path.join(dir, new_base_name)
    print('converting %s \r\n <= %s' % (new_path, old_path))
    os.chdir(dir)
    if os.path.exists(base):
        os.rename(base, new_base_name)

def main(files, dbname):
    product_map = GigaProductMap()
    database = GigaDatabase(dbname)
    product_map.load_from_database(database)
    for file in files:
        get_file_info(unicode(file, 'utf-8'), product_map)

if __name__ == '__main__':
    if not sys.argv:
        sys.exit('')
    if sys.argv[1] == '-l':
        file_list = open(sys.argv[2], 'r')
        files = file_list.readlines()
    else:
        files = sys.argv[1:]
    main(files, 'giga.db')
