#!/bin/bash

## If we have no args, make sure we use the original logging configuration
#if (($# == 0)); then
#    echo "No args, compiling default logging..."
#    echo "If you want debug logging, restart with '-d'"
#    zip -d ~/bin/DynamoDB.local/DynamoDBLocal.jar log4j2.xml
#    cp ~/bin/DynamoDB.local/log4j2-src.xml ~/bin/DynamoDB.local/log4j2.xml
#    zip -u ~/bin/DynamoDB.local/DynamoDBLocal.jar ~/bin/DynamoDB.local/log4j2.xml
#fi

## If we specify -d then compile in the debug logging before starting
#while getopts ":d" opt; do
#    case $opt in
#        d)
#            echo "Setting debug: removing default logging" >&2
#            zip -d ~/bin/DynamoDB.local/DynamoDBLocal.jar log4j2.xml
#            echo "Adding debug logging" >&2
#            cp ~/bin/DynamoDB.local/log4j2-debug.xml ~/bin/DynamoDB.local/log4j2.xml
#            zip -u ~/bin/DynamoDB.local/DynamoDBLocal.jar ~/bin/DynamoDB.local/log4j2.xml
#            ;;
#        \?)
#            echo "Invalid option: -$OPTARG" >&2
#            ;;
#    esac
#done

docker run \
       -it \
       --rm \
       -v $(pwd):/srv \
       -v $HOME/.aws/credentials:/root/.aws/credentials \
       --env PYTHONPATH=$PYTHONPATH:./python/botocore_amazon \
       --env AWS_DEFAULT_REGION=eu-west-1 \
       -p 8080:8080 \
       3c0894387697
