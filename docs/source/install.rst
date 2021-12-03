Installing RfHub2
=================

As python package
^^^^^^^^^^^^^^^^^

latest version can be installed from PyPi:

::

    pip install rfhub2

or directly from source code:

::

    python setup.py install

With docker
^^^^^^^^^^^

pull docker image with SQLite:

::

    docker pull pbylicki/rfhub2

or PostgreSQL:

::

    docker pull pbylicki/rfhub2:postgres

With helm chart
^^^^^^^^^^^^^^^

create app on kubernetes cluster

::

    helm upgrade --install rfhub2 helm/rfhub2 -n [NAMESPACE]


will create all needed resources with configuration from [values.yaml](helm/rfhub2/values.yaml)
