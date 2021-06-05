#!/bin/bash
token='amy10260903:RxlNK5vY6s0M'
repo='label-toolkit-backend'

echo "****** Getting latest for" $repo "******"
cd "Cosine/$repo"
git pull https://$token@github.com/amy10260903/$repo --rebase
#git checkout feature