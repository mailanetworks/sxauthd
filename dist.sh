#!/bin/sh
VER=0.5
set -e
# remove ignored files
git clean -X -f -d
cd src
export VERSION=`git describe --always --dirty`
python2 setup.py bdist_egg --exclude-source-files
cp dist/*.egg ../dist/
cd ..
#(cd examples/py26 && sudo docker build -t py26dist .)
#sudo docker run -v `pwd`/:/usr/src/sxauthd -e VERSION=`git describe --always --dirty` py26dist
#cp src/dist/*.egg dist/

rm -f sxauthd.tar.gz
SXAUTHD=sxauthd-$VER
tar --group=root --owner=root --transform "s,^dist,$SXAUTHD," -czf $SXAUTHD.tar.gz dist/
echo "Created $SXAUTHD.tar.gz"
tar tvf $SXAUTHD.tar.gz
echo "sxcp $SXAUTHD.tar.gz sx://indian.skylable.com/vol-skylable/customers/$SXAUTHD.tar.gz && s3cmd signurl -c ../libres3.s3cfg s3://vol-skylable/customers/$SXAUTHD.tar.gz `date +%s -d '1 month'` | sed -e 's/http:/https:/'"
