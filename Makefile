# update version in setup.py

# https://github.com/jinhangjiang/Your-First-Python-Package-on-PyPI
all: clean build-py install

clean:
	@rm -rf build/ dist/ *.egg-info
	@echo "Cleaned up"

# build
b: clean
	python setup.py build sdist bdist_wheel
	pip install .

upload:
	# https://packaging.python.org/en/latest/tutorials/packaging-projects/	
	twine upload dist/*

test:
	@python py_kvstore/test.py

version:
	@pip show python-ibc
