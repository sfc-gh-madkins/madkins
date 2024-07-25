#!/bin/zsh
NAME=$0
K8S_CONTROL="SFROLE=snowservices"
if [[ ("$#" -ne 3) && ("$#" -ne 5) ]]
then
   echo "usage: $NAME <local_port> <snowservice id> <service_port>"
   echo "or"
   echo "usage: $NAME <local_port> <service db> <service schema> <service name> <service port>"
   exit 100
fi
LOCAL_PORT=$1
if [[ ("$#" -eq 3) ]]
then
   NS_ID=$2
   SERVICE_PORT=$3
else
   S_DB=$2
   S_SCHEMA=$3
   S_NAME=$4
   NS_ID=$(snowsql -c temptest -o "header=False" -o "timing=False" -o "friendly=False" -o "output_format=plain" -q "SELECT resource_id FROM servicesnow.utilities.get_service_internal_info WHERE db_name = Upper('$S_DB') AND schema_name = Upper('$S_SCHEMA') AND service_name = Upper('$S_NAME') LIMIT 1")
   SERVICE_PORT=$5
fi
NS="rs"$NS_ID
INT_PORT=$(( $RANDOM % 20000 + 2000 ))
echo "Getting Service Namespace"
REMOTE_PORT=$(tsh ssh --cluster sfc-or-dev-temptest3 $K8S_CONTROL "echo done")
NAMESPACE=$(tsh ssh --cluster sfc-or-dev-temptest3 $K8S_CONTROL "X=\$(ps -ef | grep $NS | grep service/service | grep -v grep| awk '{ print \$2}');[[ \$X == '' ]] || kill -9 \$X;kubectl get namespaces | grep $NS | cut -d' ' -f 1" | head -1)
echo $NAMESPACE
$(sleep 3;x=$(curl localhost:$LOCAL_PORT /dev/null 2>&1);sleep 3;open -a "Google Chrome" "http://localhost:$LOCAL_PORT") &
echo "\nThis command is blocking; Type ctrl-c to exit"
tsh ssh --cluster sfc-or-dev-temptest3 -L ${LOCAL_PORT}:localhost:${INT_PORT} $K8S_CONTROL kubectl port-forward -n $NAMESPACE service/service ${INT_PORT}:${SERVICE_PORT}
