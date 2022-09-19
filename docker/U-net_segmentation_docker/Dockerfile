FROM ubuntu:20.04 AS builder
# Download and install conda into /usr/bin
ENV MINICONDA_VERSION=py37_4.10.3
RUN apt-get update && apt-get -y install --no-install-recommends \
    ca-certificates \
    curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sL https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh -o /tmp/miniconda.sh && \
# Use MD5 to do hash check  
    echo 9F186C1D86C266ACC47DBC1603F0E2ED /tmp/miniconda.sh | md5sum --status -c - && \
    if [ $? -ne 0 ]; then echo miniconda.sh has invalid md5 sum; exit 1; fi && \
# Run miniconda.sh if no error
    sh /tmp/miniconda.sh -bfp /usr && \
# install mamba
    conda install mamba -n base -c conda-forge
RUN conda update -n base -c defaults conda && \
    conda install -c conda-forge efficientnet-pytorch && \
    conda install -c conda-forge numpy && \
    conda install -c conda-forge backcall && \
    conda install -c conda-forge cycler && \
    conda install -c conda-forge decorator  && \
    conda install -c conda-forge h5py

RUN conda install -c conda-forge docker-py && \
    conda install -c conda-forge imageio && \
    conda install -c conda-forge ipython && \
    conda install -c conda-forge jedi && \
    conda install -c conda-forge kiwisolver && \
    conda install -c conda-forge matplotlib && \
    conda install -c conda-forge matplotlib-inline && \
    conda install -c conda-forge munch && \
    conda install -c conda-forge networkx && \
    conda install -c conda-forge parso && \
    conda install -c conda-forge pandas

RUN conda install -c conda-forge pexpect && \
    conda install -c conda-forge pickleshare && \
    conda install -c conda-forge pillow && \
    conda install -c conda-forge prompt-toolkit && \
    conda install -c conda-forge regex && \
    conda install -c conda-forge pretrainedmodels && \
    conda install -c conda-forge prompt-toolkit && \
    conda install -c conda-forge ptyprocess && \
    conda install -c conda-forge pygments && \
    conda install -c conda-forge pyparsing && \
    conda install -c conda-forge python-dateutil && \
    conda install -c conda-forge pyWavelets && \
    conda install -c conda-forge scikit-image && \
    conda install -c conda-forge scipy 

RUN conda install -c conda-forge segmentation-models-pytorch && \
    conda install -c conda-forge six && \
    conda install -c conda-forge tifffile && \
    conda install -c conda-forge timm && \
    conda install -c conda-forge pytorch && \
    conda install -c pytorch torchaudio && \
    conda install -c pytorch-lts torchvision

RUN conda install -c conda-forge tqdm && \
    conda install -c conda-forge traitlets && \
    conda install -c conda-forge typing-extensions && \
    conda install -c conda-forge wcwidth && \
    conda install -c conda-forge pip

Run pip3 install zernike==0.0.32
