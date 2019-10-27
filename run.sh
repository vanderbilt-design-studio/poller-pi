#!/bin/bash

# https://stackoverflow.com/questions/59895/get-the-source-directory-of-a-bash-script-from-within-the-script-itself
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Don't run heroku if on Travis
if [ -z "$CONTINUOUS_INTEGRATION" ]; then
    # https://stackoverflow.com/questions/592620/how-to-check-if-a-program-exists-from-a-bash-script
    X_API_KEY=`command -v heroku 2>/dev/null 1>&2 && heroku config:get X_API_KEY -a vanderbilt-design-studio || echo $X_API_KEY`
else
    X_API_KEY=''
fi

X_API_KEY=$X_API_KEY python "$DIR/main.py"