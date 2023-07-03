###########
# BUILDER #
###########

FROM python:3 as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

RUN pip3 install --upgrade pip

RUN mkdir -p /wheels

ADD requirements.txt .
RUN pip3 wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

#########
# FINAL #
#########

FROM python:3

RUN apt-get update && \
    apt-get install -y \
    binutils \
    bzip2 \
    libgl1 \
    libgtk-3-0 \
    libglu1 \
    libproj-dev \
    gdal-bin \
    ncat \
    postgresql-client \
    wget

# * Explicit postgresql 15 version install
# ! Must be compatible with docker-compose.yml/docker-compose.dev.yml postgres image version
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update --allow-releaseinfo-change && \
    apt-get -y install postgresql-client-15

ENV USER_NAME "spoolio_web_user"
ENV HOME_DIR "/home/${USER_NAME}"

RUN useradd -d "${HOME_DIR}" -ms /bin/bash ${USER_NAME}
USER ${USER_NAME}

RUN mkdir -p ${HOME_DIR}/app

RUN pip3 install --upgrade pip

# prusa-slicer
#  - download, extract, rename extracted dir and remove .tar
RUN cd ${HOME_DIR} && \
    wget -O PrusaSlicer.tar https://github.com/prusa3d/PrusaSlicer/releases/download/version_2.5.2/PrusaSlicer-2.5.2+linux-x64-GTK3-202303231201.tar.bz2 && \
    tar xvjf PrusaSlicer.tar && \
    mv PrusaSlicer-2.5.2+linux-x64-GTK3-202303231201 PrusaSlicer && \
    rm -r PrusaSlicer.tar

ENV PATH="${HOME_DIR}/.local/bin:${HOME_DIR}/PrusaSlicer:${PATH}"

COPY --from=builder --chown=${USER_NAME}:${USER_NAME} /wheels ${HOME_DIR}/wheels
RUN pip3 install --user --no-cache ${HOME_DIR}/wheels/*

RUN chown -R ${USER_NAME}:${USER_NAME} ${HOME_DIR}

WORKDIR ${HOME_DIR}/app
