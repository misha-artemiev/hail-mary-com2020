#!/usr/bin/env bash
read -s -p "GitHub Personal Access Token: " GITHUB_TOKEN
kubectl create secret docker-registry ghcr-secret -n hail-mary \
  --docker-server=ghcr.io \
  --docker-username=misha-artemiev \
  --docker-password="$GITHUB_TOKEN" \
  --docker-email="github-actions[bot]@users.noreply.github.com" \
  --dry-run=client -o yaml | kubectl apply -f -
unset GITHUB_TOKEN
