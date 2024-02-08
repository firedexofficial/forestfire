FROM registry.gitlab.com/packaging/signal-cli/signal-cli-native:latest as signal
RUN signal-cli --version | tee /tmp/signal-version

FROM python:3.10 as libbuilder
WORKDIR /app
RUN pip install poetry
RUN python3.10 -m venv /app/venv
COPY pyproject.toml poetry.lock /app/
RUN VIRTUAL_ENV=/app/venv poetry install

FROM ubuntu:latest
WORKDIR /app
RUN mkdir -p /app/data
RUN apt-get update && apt-get install -y python3.10
RUN apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/
COPY --from=signal /usr/bin/signal-cli-native /app/signal-cli
COPY --from=signal /tmp/signal-version /app/
# for signal-cli's unpacking of native deps
COPY --from=signal /lib/x86_64-linux-gnu/libz.so.1 /lib64
COPY --from=libbuilder /app/venv/lib/python3.10/site-packages /app/
COPY ./forest /app/forest
COPY ./mc_util /app/mc_util
COPY .git/COMMIT_EDITMSG CHANGELOG.md hellobot.py /app/
ENTRYPOINT ["/usr/bin/python3.10", "/app/hellobot.py"]
