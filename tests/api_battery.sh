#!/usr/bin/env bash

USER="$1"

register_cases=(
    # fresh user
    '-F organization=Primal -F username='"${USER}"' -F password=easY123!'

    # bad org
    '-F organization=Swimal -F username='"${USER}"' -F password=easY123!'

    # already existing user
    '-F organization=Primal -F username='"${USER}"' -F password=easY123!'

    # weak pass
    '-F organization=Primal -F username=dylan -F password=breakable'
)

login_cases=(
    # good login
    '-F organization=Primal -F username='"${USER}"' -F password=easY123!'

    # bad org
    '-F organization=Swimal -F username='"${USER}"' -F password=easY123!'

    # nonexistent user
    '-F organization=Primal -F username=yorkshire -F password=easY123!'

    # bad pass
    '-F organization=Primal -F username='"${USER}"' -F password=asdfasdf'
)

echo -e "\nRegistration Testing"
for tc in "${register_cases[@]}"; do
    eval "curl -X POST ${tc} localhost:3005/auth/register" && echo
done && echo 

echo "Login Testing"
for tc in "${login_cases[@]}"; do
    eval "curl -X POST ${tc} localhost:3005/auth/login" && echo
done && echo