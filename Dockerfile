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

RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    ncat \
    postgresql-client

ENV USER_NAME "spoolio_web_user"
ENV HOME_DIR "/home/${USER_NAME}"

RUN useradd -d "${HOME_DIR}" -ms /bin/bash ${USER_NAME}
USER ${USER_NAME}

RUN mkdir -p ${HOME_DIR}/app

RUN pip3 install --upgrade pip

ENV PATH="${HOME_DIR}/.local/bin:${PATH}"

COPY --from=builder --chown=${USER_NAME}:${USER_NAME} /wheels ${HOME_DIR}/wheels
RUN pip3 install --user --no-cache ${HOME_DIR}/wheels/*

RUN chown -R ${USER_NAME}:${USER_NAME} ${HOME_DIR}

WORKDIR ${HOME_DIR}/app

COPY ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]