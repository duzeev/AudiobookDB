#/bin/bash

source ./conf-linux.sh

cd AudioBookSiteFlask/static
ln -s $DIR_ZIP zip
ln -s $DIR_PIC pic
cd ../..

cd AudioBookSiteDjango/AudioBook/static
ln -s $DIR_ZIP zip
ln -s $DIR_PIC pic
cd ../../..

