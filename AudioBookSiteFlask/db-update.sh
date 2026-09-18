#/bin/bash
source ../conf-linux.sh

source ../AudioBookSiteDjango/.venv/bin/activate

python3 db-update.py $DIR_ZIP $DIR_PIC