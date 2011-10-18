#!/bin/sh
rm -f `find . -name "*.sw?"` 2> /dev/null
rm -f `find . -name "*.pyc"` 2> /dev/null
rm -f `find . -name "*.orig"` 2> /dev/null
rm -f `find . -name ".tmp_*"` 2> /dev/null
rm -rf windows 2> /dev/null
