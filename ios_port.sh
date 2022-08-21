#!/bin/sh
iproxy 2222 22 > /dev/null 2>&1 &
iproxy 1234 1234 > /dev/null 2>&1 &
iproxy 7788 7788 > /dev/null 2>&1 &
iproxy 52734 52734 > /dev/null 2>&1 &
