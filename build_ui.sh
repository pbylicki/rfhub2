#!/bin/bash
# !!!Please use clean paramater for this bash script if you need to clean static files.!!!
pushd frontend
yarn build
popd
if [ "$1" == "clean" ]; then
    rm -r rfhub2/static/*
    rm rfhub2/templates/index.html
fi
cp -r frontend/build/* rfhub2/static
mv rfhub2/static/index.html rfhub2/templates/index.html