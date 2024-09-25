##########################################################################################
#
#   DESCRIPTION:  Development Docker Container.  Installs the following:
#                 * miniconda
#                 * Oh-My-Zsh
#                 * awesome-vim
#
#   GPU SUPPORT:  In order to get GPU support the nvidia image's CUDA version must
#                 match the version on the host computer.
#
#     RENDERING:  If rendering to the screen is required then execute the following
#                 prior to starting the container:
#
#                 ```console
#                 xhost +local:root
#                 ```
#
#        AUTHOR:  W. Li
#       VERSION:  1.0
#       CREATED:  12/15/2023
##########################################################################################

# Source Image (this should match the CUDA version on the host)
# FROM nvidia/cuda:11.4.1-base-ubuntu20.04
FROM ubuntu:20.04

# Labels
LABEL version="1.0"
LABEL description="Miniconda Dev Image"

# Expose ports here
# EXPOSE 8080

# Install basic packages needed for development
RUN yes Y | apt update
RUN yes Y | apt-get update
RUN yes Y | apt upgrade
RUN yes Y | apt install vim
RUN apt-get install -y --no-install-recommends \
    git \
    wget \
    g++ \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Setup shell
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.1/zsh-in-docker.sh)" -- \
    -t robbyrussell \
    -p git -p ssh-agent -p 'history-substring-search' \
    -a 'bindkey "\$terminfo[kcuu1]" history-substring-search-up' \
    -a 'bindkey "\$terminfo[kcud1]" history-substring-search-down'

# Setup Shell
SHELL ["/bin/zsh", "-c"]

# Miniconda requires that the path point to its python binary
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

# Source python versions: https://repo.anaconda.com/miniconda/
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

RUN conda init zsh

# Setup Vim-Awesome
RUN git clone --depth=1 https://github.com/amix/vimrc.git ~/.vim_runtime \
    && sh ~/.vim_runtime/install_basic_vimrc.sh

# Setup working directory
WORKDIR /projects

# Copy folder/files into container (must be within context directory)
# Process: local files -> artifact dir -> container dir
# COPY <local_path> <container_path>

# Environment
ENV SHELL /bin/zsh
