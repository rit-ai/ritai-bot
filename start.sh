#!/bin/bash

if [ -z $APP_ROOT ]; then export APP_ROOT=`pwd`; fi

cd $APP_ROOT
source $APP_ROOT/bin/activate

if [ -f driver.py ]; then
    python3 driver.py
else
    python3 driver.env.py
fi
