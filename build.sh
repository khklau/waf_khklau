#!/bin/sh

HERE=`readlink -m $0 | xargs dirname`

EXTRAS=`ls -1 ${HERE}/waflib/extras/ | grep "\.py$" | sed 's/\.py$//g' | tr "\n\r" "," | sed 's/,$//g'`
(
    if [ -e "${HERE}/waf" ]; then rm -f ${HERE}/waf; fi && \
    ./waf-light --make-waf --tools=${EXTRAS} configure build && \
    ./waf-light clean distclean
)
