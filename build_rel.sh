#!/bin/bash
# make a release build
# output is located at releases/ehsyringe.user.js
pnpm exec webpack --mode=production --env type=user-script
