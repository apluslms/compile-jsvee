FROM apluslms/compile:python3-0.1

ARG VERSION=563075c9b486295586323c0cff3db582ffda1f40
ARG DIR=jsvee-$VERSION

RUN mkdir -p /work/ /opt/jsvee/ && cd /opt/jsvee/ \
 && curl -LSs https://github.com/Aalto-LeTech/jsvee/archive/$VERSION.tar.gz | tar -zx \
 && cat $DIR/core.js \
        $DIR/messages.js \
        $DIR/ui_utils.js \
        $DIR/actions.js \
        $DIR/ui.js \
        > engine.js \
 && mkdir kelmu && cp $DIR/kelmu.js kelmu \
 && mkdir scala && cp $DIR/scala/*.png $DIR/scala/*.json $DIR/scala/*.css $DIR/scala/*.js scala \
 && mkdir python && cp $DIR/python/*.css $DIR/python/*.js python \
 && cp -r $DIR/pics \
          $DIR/messages_fi.json \
          $DIR/jsvee.css . \
 && rm -r $DIR

COPY collect.py config.yml template.js /opt/
COPY offline.js /opt/jsvee/

ENTRYPOINT ["python3", "/opt/collect.py"]
CMD ["-f", "html/_static/jsvee/"]
