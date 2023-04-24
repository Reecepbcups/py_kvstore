# docker build . -t py_kvstore

# build the current python repo and ensure a successful compile and test
FROM python:3.11.2

# install the python repo
COPY . /py_kvstore

# install the python repo
RUN pip install /py_kvstore

# run the tests
# RUN ls /py_kvstore

# run the test to ensure docker is good
RUN python /py_kvstore/py_kvstore/test.py