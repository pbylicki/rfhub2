#!/bin/bash
pushd frontend
yarn build
popd
rm -r rfhub2/static/*
rm rfhub2/templates/index.html
cp -r frontend/build/* rfhub2/static
mv rfhub2/static/index.html rfhub2/templates/index.html