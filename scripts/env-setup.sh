#!/bin/bash

mkdir ~/bin
mkdir -p ~/lib/python
echo -e 'export PYTHONPATH=${HOME}/lib/python:$PYTHONPATH\nexport PATH=${HOME}/bin:$PATH' >> ~/.bash_profile
source ~/.bash_profile  
curl "http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz#md5=7df2a529a074f613b509fb44feefe74e" > setuptools-0.6c11.tar.gz
tar -xf setuptools-0.6c11.tar.gz
cd setuptools-0.6c11
python setup.py build
python setup.py install --home=~
cd ..
easy_install --install-dir=~/lib/python/ pip
~/lib/python/pip install --install-option="--home=~" boto
~/lib/python/pip install --install-option="--home=~" argparse
rm -rf setuptools-0.6c11
rm setuptools-0.6c11.tar.gz