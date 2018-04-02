#!/bin/sh

curl -L -c giga-web.cookie.jar https://www.giga-web.jp/cookie_set.php > cookie_set.php

for i in `seq $2 $1`; do
	echo get $i
	curl -b giga-web.cookie.jar 'https://www.giga-web.jp/product/index.php?menu=1&product_id='$i > $i.html
done
