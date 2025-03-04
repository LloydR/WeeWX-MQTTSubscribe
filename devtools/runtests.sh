#! /bin/bash
#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
if [ -z "$1" ]
then
    WEEWX=weewx4
else
    WEEWX=$1
fi

# Note, the value for $WEEWX can be relative. For example ../weewx-source/weewx-3.7.1

echo "Running python $PYENV_VERSION weewx $WEEWX"
PYTHONPATH=bin:../$WEEWX/bin python -m unittest discover bin/user/tests/unit

PYTHONPATH=bin:../$WEEWX/bin python -m unittest discover bin/user/tests/integ

echo "Completed python $PYENV_VERSION weewx $WEEWX"
