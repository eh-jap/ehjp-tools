#!/bin/bash
# partial rebuilds when sources changed, interrupt with ^C
pnpm exec webpack --mode=development --watch --env type=user-script
