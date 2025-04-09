FROM tensorflow/tensorflow:2.11.0

RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
--mount=target=/var/cache/apt,type=cache,sharing=locked \
rm -f /etc/apt/apt.conf.d/docker-clean && \
apt-get update && \
apt-get install ffmpeg libsm6 libxext6 -y

ADD ./requirements.txt .
RUN /usr/bin/python3 -m pip install --upgrade pip && \
pip install -r requirements.txt

ADD . .

CMD [ "flask", "--app", "hairstyler", "run", "--cert=certificates/cert.pem", "--key=certificates/key.pem", "--host=0.0.0.0" ]
