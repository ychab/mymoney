#!/bin/bash

# Should be launched by cron (every nights)
# How to use : /path/to/scripts/clonescheduled.sh /path/to/v_env

if [ "$1" == "" ]
then
  echo "ERROR : Virtualenv path is required"
  exit 1
else
  V_ENV_PATH=$1
fi

source "$V_ENV_PATH"/bin/activate

cd "$(dirname "$0")/.."

python manage.py clonescheduled --settings=mymoney.settings.production

deactivate

logger "[MYMONEY] Scheduled bank transactions cloned."
