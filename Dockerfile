FROM debian:stretch-slim

ENV LANG=C.UTF-8

RUN apt-get update -qqy && DEBIAN_FRONTEND=noninteractive apt-get install -qqy --no-install-recommends \
    -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
    python3 \
    python3-yaml \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
  && mkdir -p /work/

COPY collect_jsvee.py template.js /

WORKDIR /work/
ENTRYPOINT ["python3", "/collect_jsvee.py"]
CMD ["-f", "build/animaatiot/jsvee/JSVEE.js"]
