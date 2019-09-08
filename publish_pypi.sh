python setup.py sdist bdist_wheel
twine upload dist/*
rm -rf build dist rfhub2.egg-info