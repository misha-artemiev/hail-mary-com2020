#!/bin/bash
read -s -p "postgres password: " PG_PASSWORD
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: hail-mary-postgres-secret
  namespace: hail-mary
type: Opaque
stringData:
  username: hail-mary
  password: $PG_PASSWORD
EOF
unset PG_PASSWORD
