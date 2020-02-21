#!/bin/bash

if [ -z $APP_ROOT ]; then export APP_ROOT=`pwd`; fi

cd $APP_ROOT
source $APP_ROOT/bin/activate

python3 driver.py
