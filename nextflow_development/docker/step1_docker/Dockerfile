### STEP 1 DOCKERFILE
FROM ubuntu:20.04 AS builder

RUN  apt-get update \
   &&  apt-get -y install python3 \
   # install pip
    &&  apt-get -y install python3-pip 

ENV PATH /usr/local/bin:$PATH

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
    wcwidth==0.2.5 \
    && mkdir /hslci_pipeline_supplementary
COPY final_unet_checkpoint.pkl /hslci_pipeline_supplementary
COPY step1_segment.py /hslci_pipeline_supplementary

# # Download and install conda into /usr/bin
# ENV MINICONDA_VERSION=py38_4.11.0
# RUN apt-get update && apt-get -y install --no-install-recommends \
#     ca-certificates \
#     curl && \
#     rm -rf /var/lib/apt/lists/* && \
#     curl -sL https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh -o /tmp/miniconda.sh && \
# # Use MD5 to do hash check  
#     # echo 9F186C1D86C266ACC47DBC1603F0E2ED /tmp/miniconda.sh | md5sum --status -c - && \
#     # if [ $? -ne 0 ]; then echo miniconda.sh has invalid md5 sum; exit 1; fi && \
# # Run miniconda.sh if no error
#     sh /tmp/miniconda.sh -bfp /usr && \
# # install mamba
#     conda install mamba -n base -c conda-forge
# RUN conda update -n base -c defaults conda && \
#     conda install -c conda-forge efficientnet-pytorch && \
#     conda install -c conda-forge numpy && \
#     conda install -c conda-forge backcall && \
#     conda install -c conda-forge cycler && \
#     conda install -c conda-forge decorator  && \
#     conda install -c conda-forge h5py

# RUN conda install -c conda-forge docker-py && \
#     conda install -c conda-forge imageio && \
#     conda install -c conda-forge ipython && \
#     conda install -c conda-forge jedi && \
#     conda install -c conda-forge kiwisolver && \
#     conda install -c conda-forge matplotlib && \
#     conda install -c conda-forge matplotlib-inline && \
#     conda install -c conda-forge munch && \
#     conda install -c conda-forge networkx && \
#     conda install -c conda-forge parso && \
#     conda install -c conda-forge pandas

# RUN conda install -c conda-forge pexpect && \
#     conda install -c conda-forge pickleshare && \
#     conda install -c conda-forge pillow && \
#     conda install -c conda-forge prompt-toolkit && \
#     conda install -c conda-forge regex && \
#     conda install -c conda-forge pretrainedmodels && \
#     conda install -c conda-forge prompt-toolkit && \
#     conda install -c conda-forge ptyprocess && \
#     conda install -c conda-forge pygments && \
#     conda install -c conda-forge pyparsing && \
#     conda install -c conda-forge python-dateutil && \
#     conda install -c conda-forge pyWavelets && \
#     conda install -c conda-forge scikit-image && \
#     conda install -c conda-forge scipy 

# RUN conda install -c conda-forge segmentation-models-pytorch && \
#     conda install -c conda-forge six && \
#     conda install -c conda-forge tifffile && \
#     conda install -c conda-forge timm && \
#     conda install -c conda-forge pytorch && \
#     conda install -c pytorch torchaudio && \
#     conda install -c pytorch-lts torchvision

# RUN conda install -c conda-forge tqdm && \
#     conda install -c conda-forge traitlets && \
#     conda install -c conda-forge typing-extensions && \
#     conda install -c conda-forge wcwidth && \
#     conda install -c conda-forge pip

# Runqw pip3 install zernike==0.0.32
