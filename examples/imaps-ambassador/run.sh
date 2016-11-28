#!/bin/sh
# Replace IMAPS_SERVER with your imap server (port 993)
docker rm -f imaps-ambassador-run
exec docker run -d --name imaps-ambassador-run --restart=always -e IMAPS_SERVER=zimbra.skylable.com  imaps-ambassador
