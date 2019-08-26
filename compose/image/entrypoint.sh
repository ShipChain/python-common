#!/bin/bash

USER_ID=${LOCAL_USER_ID:0}
GROUP_ID=${LOCAL_GROUP_ID:0}
echo "Starting with GUID:UID : $GROUP_ID:$USER_ID"
if [[ USER_ID -ne 0 ]];
then
    addgroup -g $GROUP_ID -S username && adduser -u $USER_ID -S username -G username
fi

if [[ ! -f $VIRTUAL_ENV/bin/python ]];
then
    echo "Creating virtualenv"
    su-exec $USER_ID:$GROUP_ID virtualenv $VIRTUAL_ENV
fi

exec su-exec $USER_ID:$GROUP_ID "$@"