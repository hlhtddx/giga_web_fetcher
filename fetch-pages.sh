#!/bin/sh

DIR=`dirname $0`
curl -L -c giga-web.cookie.jar https://www.giga-web.jp/cookie_set.php > cookie_set.php

for i in `seq $1 $2`; do
	echo get $i
	curl -b giga-web.cookie.jar 'https://www.giga-web.jp/product/index.php?menu=1&product_id='$i > ${DIR}/data/$i.html
done
