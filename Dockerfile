FROM apluslms/compile-python

ARG VERSION=73897f42b9c85aa8edf72e2d06b6db6a193b2e2e
ARG DIR=jsvee-$VERSION

RUN mkdir -p /work/ /opt/jsvee/ && cd /opt/jsvee/ \
 && curl -LSs https://github.com/Aalto-LeTech/jsvee/archive/$VERSION.tar.gz -o jsvee.tar.gz \
 && tar -zxf jsvee.tar.gz \
 && cat $DIR/core.js \
        $DIR/actions.js \
        $DIR/messages.js \
        $DIR/ui_utils.js \
        $DIR/ui.js \
        $DIR/kelmu.js \
        > engine.js \
 && cp -r $DIR/pics $DIR/jsvee.css . \
 && rm -r $DIR jsvee.tar.gz

COPY collect.py config.yml template.js /opt/

WORKDIR /work/
ENTRYPOINT ["python3", "/opt/collect.py"]
CMD ["-f", "html/_static/jsvee/"]
