THIS_FILE := $(lastword $(MAKEFILE_LIST))

build:
	@$(MAKE) -f $(THIS_FILE) clean 
	python3 setup.py sdist bdist_wheel
upload:
	python3 -m twine upload dist/*
clean:
	rm -rf *.egg-info/
	rm -rf dist/
	rm -rf build/
