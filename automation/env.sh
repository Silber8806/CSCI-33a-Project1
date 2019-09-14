#!/bin/bash

env_script=${BASH_SOURCE[0]}
env_select=$1

env_dir=$(dirname $env_script)
env_secrets=$(echo $env_dir | awk -F '/' 'BEGIN { OFS="/";}{ $(NF)="secrets"; print $0;}')

echo "trying to source: ${env_secrets}/${env_select}.config"

if [[ "x${env_select}" = "x" ]]
then
    echo "bad parameter"
fi

dev_key="${env_secrets}/dev.config"
test_key="${env_secrets}/test.config"
prod_key="${env_secrets}/prod.config"

if [[ "${env_select}" = "dev" && -f "${dev_key}" ]]
then
    echo "using dev settings"
    source ${dev_key}
elif [[ "${env_select}" = "test" && -f "${test_key}" ]]
then
    echo "using test settings"
    source ${test_key}
elif [[ "${env_select}" = "prod" && -f "${prod_key}" ]]
then
    echo "using production settings"
    source ${prod_key}
else
    echo "no environment found..."
fi

echo "exporting parameters"
export FLASK_APP
export FLASK_DEBUG
export DATABASE_URL
export DATABASE_HOST
export DATABASE
export DATABASE_USER
export DATABASE_PASSWORD
