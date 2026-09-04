#!/bin/bash
# run in the "Database" repo
# run ./scripts/init.sh before this for first time dev
# it generates many files but only "db.html.json" is used by us
# other files is probably for different type of clients
node --enable-source-maps tool create-release . ./publish
