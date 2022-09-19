FROM ubuntu:20.04

RUN sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list \
   &&  apt-get update \
   &&  apt-get -y install --no-install-recommends \


RUN mkdir /src/ \
   && mkdir /src/script/

WORKDIR /src/script/

COPY step1_files /src/script/
COPY step1_segment.py /src/script/

# Define default command
CMD ["/bin/bash"]