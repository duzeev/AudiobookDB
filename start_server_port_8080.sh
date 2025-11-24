#/bin/bash

source ./AudioBookSite/.venv/bin/activate

authbind --deep python3 server.py 8080

