FROM python:3.6-alpine

COPY requirements*.txt /tmp/

RUN apk add --no-cache --virtual .build-deps gcc musl-dev make && \
    pip install --disable-pip-version-check --no-cache-dir -r /tmp/requirements.txt && \
    apk del .build-deps && \
    rm /tmp/requirements*.txt && \
    mkdir /app && \
    chown 1001:1001 /app

COPY --chown=1001 rfhub2 /app/rfhub2

WORKDIR /app

USER 1001

CMD ["python", "-m", "rfhub2"]