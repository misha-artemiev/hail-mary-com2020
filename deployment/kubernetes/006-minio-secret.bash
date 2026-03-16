#!/bin/bash
read -s -p "minio secret key: " MINIO_SECRET_KEY
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: hail-mary-minio-secret
  namespace: hail-mary
type: Opaque
stringData:
  access-key: hail-mary-block
  secret-key: $MINIO_SECRET_KEY
EOF
unset MINIO_SECRET_KEY
