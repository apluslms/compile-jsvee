A docker container that collects JSVEE animation files and combines them to single javascript.

.. code-block:: sh

    docker run --rm \
      --mount type=tmpfs,destination=/work,tmpfs-size=100M \
      -v $(pwd)/_build:/work/build \
      -v $(pwd):/work/src:ro \
      -w /work \
      -u $(id -u):$(id -g) \
      apluslms/compile-jsvee
