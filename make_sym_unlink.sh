#/bin/bash

source ./conf-linux.sh

cd AudioBookSiteFlask/static
unlink zip
unlink pic
cd ../..

cd AudioBookSiteDjango/AudioBook/static
unlink zip
unlink pic
cd ../../..
