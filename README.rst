======================
youtube-video-downloader
======================

.. image:: https://img.shields.io/pypi/v/mnlvm_video_downloader.svg
        :target: https://pypi.python.org/pypi/mnlvm_video_downloader

.. image:: https://img.shields.io/travis/masterivanic/mnlvm_video_downloader.svg
        :target: https://travis-ci.com/masterivanic/mnlvm_video_downloader

.. image:: https://readthedocs.org/projects/mnlvm-video-downloader/badge/?version=latest
        :target: https://mnlvm-video-downloader.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/masterivanic/mnlvm_video_downloader/shield.svg
        :target: https://pyup.io/repos/github/masterivanic/mnlvm_video_downloader/
        :alt: Updates

A simple Python project that allows users to download individual YouTube videos or entire playlists.

* Free software: BSD license
* Documentation: https://youtube-video-downloader.readthedocs.io

Features
--------

* Download individual YouTube videos
* Download full YouTube playlists
* Supports various video/audio quality options
* Automatically fetches metadata
* Easy-to-use CLI interface
* Compatible with Windows, macOS, and Linux

Installation
------------

Install the package using pip:

.. code-block:: bash

    pip install mnlvm_video_downloader

**Important Requirement – ffmpeg**

In order to process audio and video properly (especially when downloading or merging audio/video streams), it is **highly recommended** to install `ffmpeg` and ensure it is available in your system's PATH.

**How to install ffmpeg:**

- On Windows:
    1. Download from: https://ffmpeg.org/download.html
    2. Extract the archive and add the `bin/` folder to your system `PATH`
- On macOS:
    .. code-block:: bash

        brew install ffmpeg
- On Linux (Debian/Ubuntu):
    .. code-block:: bash

        sudo apt update
        sudo apt install ffmpeg

You can verify the installation with:

.. code-block:: bash

    ffmpeg -version

Usage
-----

After installation, you can use the CLI tool like this:

.. code-block:: bash

    mnlvm-download https://www.youtube.com/watch?v=example_video_id

Or to download a full playlist:

.. code-block:: bash

    mnlvm-download https://www.youtube.com/playlist?list=example_playlist_id

See the full documentation for more details: https://youtube-video-downloader.readthedocs.io

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
