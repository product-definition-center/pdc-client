.. _release:


Release
=======

Versioning
----------

PDC Client versioning is based on `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

And it's RPM compatible.

Given a version number MAJOR.MINOR.PATCH, increment the:

#. MAJOR version when you make incompatible API changes,
#. MINOR version when you add functionality in a backwards-compatible manner,
#. PATCH version when you make backwards-compatible bug fixing.

Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.

#. A pre-release version MAY be denoted by appending a hyphen and an identifier immediately following the patch version.

   Identifier MUST be comprised and only with ASCII alphanumerics [0-9A-Za-z].
   Identifier MUST NOT be empty.
   Numeric identifier MUST NOT include leading zeroes.
   Pre-release versions have a lower precedence than the associated normal version.
   A pre-release version indicates that the version is unstable and might not satisfy the intended compatibility requirements as denoted by its associated normal version.
   Examples: 1.0.0-alpha, 1.0.0-sprint5, 1.0.0-rc4.

#. Build metadata MAY be denoted by appending a hyphen and a series of dot separated identifiers immediately following the patch or a dot and a series of dot separated identifiers immediately following the pre-release version.

   Identifiers MUST be comprise and only with ASCII alphanumerics [0-9A-Za-z].
   Identifiers MUST NOT be empty.
   Build metadata SHOULD be ignored when determining version precedence.
   Thus two versions that differ only in the build metadata, have the same precedence.
   Examples: 1.0.0-12.g1234abc, 1.0.0-s5.4.g1234abc.


Release Instruction
-------------------

In practice, we use `tito` to add git tag and do release including tag based on releases and current HEAD based on test releases.

.. NOTE:: `tito` version >= 0.6.2, install guide refer to: `https://github.com/dgoodwin/tito`

A short instructions as:

#. Tag: ``tito tag``
#. Test Build: ``tito build --rpm ---offline``
#. Push: ``git push origin && git push origin $TAG``
#. Release: ``tito release copr-pdc/copr-pdc-test``

For each step, more detail are:

Tag
```

A new git tag need to be added before starting a new release::

    $ tito tag

It will:

- bump version or release, based on which `tagger` is used, see `.tito/tito.props`;
- create an annotated git tag based on our version;
- update the spec file accordingly, generate changelog event.

For more options about `tito tag`, run `tito tag --help`.

Test Build
``````````

Once release tag is available, we can do some build tests including source tarball checking, and rpm building testing.

   ::

    # generate local source tarball
    $ tito build --tgz --offline

    # generate local rpm build
    $ tito build --rpm --offline

If everything goes well, you could push your commit and tag to remote, otherwise the tag need to be undo::

    $ tito tag -u

.. NOTE:: During developing, we could also generate test build any time, which will be based on current `HEAD` instead of latest tag.

  ::

    # generate test builds
    $ tito build --test --tgz/srpm/rpm

Push
````

When you're happy with your build, it's time to push commit and tag to remote.

::

    $ git push origin && git push origin <your_tag>

Release To PyPI
```````````````

The Python Package Index or `PyPI <https://pypi.python.org/pypi>`_ is the official third-party software repository for the Python programming language.
Release PDC Client to PyPI make it be able to pip install this for usage in other projects.
`pdc-client <https://pypi.python.org/pypi/pdc-client>`_ was already registered in PyPI.

If you haven't created an account in PyPI or configured PyPI in local environment, you may need:

- create your account on `PyPI Live  <https://pypi.python.org/pypi?%3Aaction=register_form>`_.
- contact PDC team to get `PyPI pdc-client <https://pypi.python.org/pypi/pdc-client>`_ access.
- create  ~/.pypirc configuration file with content::

    [distutils]
    index-servers=pypi

    [pypi]
    repository = https://pypi.python.org/pypi
    username = your_username
    password = your_password

Finally, you can upload your distributions to PyPI. There are two options:

#. Use `twine <https://python-packaging-user-guide.readthedocs.org/en/latest/projects/#twine>`_.
   Twine uses only verified TLS to upload to PyPI in order to protect your credentials from theft::

        twine upload dist/*

#. **(Not recommended):** Use `setuptools <https://python-packaging-user-guide.readthedocs.org/en/latest/projects/#setuptools>`_.
   This approach is covered here due to it being mentioned in other guides,
   but it is not recommended as it may use a plaintext HTTP or unverified HTTPS connection on some Python versions,
   allowing your username and password to be intercepted during transmission.

   The command could be::

        python setup.py sdist upload


