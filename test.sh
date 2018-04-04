#!/bin/sh -e

# REMOVE AND RENAME

docker image rm apluslms/compile-jsvee:test_old || true
docker image tag apluslms/compile-jsvee:test apluslms/compile-jsvee:test_old || true

# BUILD

docker build -t apluslms/compile-jsvee:test .

# RUN COMIPILE
docker run --rm \
  --mount type=tmpfs,destination=/work,tmpfs-size=100M \
  -v $(pwd)/test/build:/work/build \
  -v $(pwd)/test/src:/work/src:ro \
  -u $(id -u):$(id -g) \
  apluslms/compile-jsvee:test

# VALIDATE
(
    cd test
    if [ -e build.md5sum ]; then
        md5sum -c --quiet build.md5sum
    else
        find build -type f|xargs md5sum > build.md5sum
    fi
)
