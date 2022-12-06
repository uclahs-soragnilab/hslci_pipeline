### STEP 1 DOCKERFILE
FROM ubuntu:20.04

RUN  apt-get update \
   &&  apt-get -y install python3 \
   # install pip
    &&  apt-get -y install python3-pip 

RUN mkdir /src/ \
   && mkdir /src/script/

WORKDIR /src/script/

RUN pip3 install efficientnet-pytorch==0.7.1 \
     && pip3 install  backcall==0.2.0 \
     cycler==0.10.0 \
     decorator==5.1.0 \
     h5py==3.6.0 \
     imageio==2.9.0 \
     ipython==7.30.1 \
     jedi==0.18.0 \
     kiwisolver==1.3.2 

RUN pip3 install matplotlib==3.5.1 \
     && pip3 install matplotlib-inline==0.1.6 

RUN pip3 install munch==2.5.0 \
    networkx==2.6.3 \
    numpy==1.21.4 \
    parso==0.8.2 \
    pandas==1.4.3 \
    pexpect==4.8.0 \
    pickleshare==0.7.5 \
    Pillow==8.4.0 \
    regex==2021.11.10 \
    pretrainedmodels==0.7.4 \
    prompt-toolkit==3.0.21

RUN pip3 install ptyprocess==0.7.0 \
     Pygments==2.10.0 \
     pyparsing==3.0.1 \
     python-dateutil==2.8.2 \
     PyWavelets==1.1.1 \
     scikit-image==0.19.0 \
     scipy==1.7.3 \
     segmentation-models-pytorch==0.2.0 \
     six==1.16.0 \
     tifffile==2021.11.2 \
     timm==0.4.12

RUN pip3 install torch==1.10.0 \
     install torchaudio==0.10.2 \
     torchvision==0.11.1 \
     tqdm==4.62.3 \
    && pip3 install typing-extensions==3.10.0.2 \
     wcwidth==0.2.5

RUN pip3 install zernike==0.0.32 \
    wcwidth==0.2.5 

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
   &&  apt-get -y install r-base
RUN R --save -e "install.packages('remotes', repos='http://cran.us.r-project.org')" \
     && R --save -e "remotes::install_version('plyr', version = '1.8.8', repos = 'http://cran.us.r-project.org')" \
     && R --save -e "remotes::install_version('dplyr', version = '1.0.7', repos = 'http://cran.us.r-project.org')" \
     && R --save -e "remotes::install_version('rpart', version = '4.1.16', repos = 'http://cran.us.r-project.org')" \
     && R --save -e "remotes::install_version('mlr3verse', version = '0.2.5', repos = 'http://cran.us.r-project.org')" \
     && R --save -e "remotes::install_version('mlr3', version = '0.13.3', repos = 'http://cran.us.r-project.org')" \
     && R --save -e "remotes::install_version('pROC', version = '1.17.0.1', repos = 'http://cran.us.r-project.org')" \
     && R --save -e "remotes::install_version('precrec', version = '0.12.8', repos = 'http://cran.us.r-project.org')" \
     && R --save -e "remotes::install_version('xgboost', version = '1.5.2.1', repos = 'http://cran.us.r-project.org')" \
     && R --save -e "remotes::install_version('mlr3viz', version = '0.5.9', repos = 'http://cran.us.r-project.org')" 

 
ADD ./hslci_data_package/ /src/script/

RUN apt-get install -y wget \
    && wget https://downloads.imagej.net/fiji/archive/20220222-1015/fiji-linux64.tar.gz \
    && tar -xvzf fiji-linux64.tar.gz \
    && rm fiji-linux64.tar.gz
 
CMD ["/bin/bash"]

# ENTRYPOINT ["/bin/bash", "-l", "-c"]
