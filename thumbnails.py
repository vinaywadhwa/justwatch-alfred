#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-10-11
#

"""Generate thumbnails in the background."""

from __future__ import print_function, unicode_literals, absolute_import

import logging
import hashlib
import os
import subprocess
import sys

from workflow import Workflow
from workflow.util import LockFile, atomic_writer

# LOG = "/tmp/ccd.log"
# logging.basicConfig(filename=LOG, filemode="w", level=logging.DEBUG)
# console = logging.StreamHandler()
# console.setLevel(logging.ERROR)
# logging.getLogger("").addHandler(console)

# logger = logging.getLogger(__name__)
wf = Workflow()

logger = wf.logger


class Thumbs(object):
    """Thumbnail generator."""
    logger = None

    def __init__(self, cachedir):
        """Create new ``Thumbs`` object.

        Args:
            cachedir (str): Path to directory to save thumbnails in.
        """
        self._cachedir = os.path.abspath(cachedir)
        self._queue_path = os.path.join(self._cachedir, 'thumbnails.txt')
        self._queue = []

        try:
            os.makedirs(self._cachedir)
        except (IOError, OSError):
            pass

    @property
    def cachedir(self):
        """Where thumbnails are saved.

        Returns:
            str: Directory path.
        """
        return self._cachedir

    def thumbnail_path(self, img_path):
        """Return appropriate path for thumbnail.

        Args:
            img_path (str): Path to image file.

        Returns:
            str: Path to thumbnail.
        """
        if isinstance(img_path, unicode):
            img_path = img_path.encode('utf-8')
        elif not isinstance(img_path, str):
            img_path = str(img_path)

        h = hashlib.md5(img_path).hexdigest()
        thumb_path = os.path.join(self.cachedir, u'{}.png'.format(h))
        return thumb_path

    def thumbnail(self, img_path):
        """Return resized thumbnail for ``img_path``.

        Args:
            img_path (str): Path to original images.

        Returns:
            str: Path to thumbnail image.
        """
        # logger.info("getting thumb path from img_path - "+img_path)
        thumb_path = self.thumbnail_path(img_path)
        # print("Got thumb path - " + thumb_path)
        if os.path.exists(thumb_path):
            return thumb_path
        else:
            self.queue_thumbnail(img_path)
            return None

    def queue_thumbnail(self, img_path):
        """Add ``img_path`` to queue for later thumbnail generation.

        Args:
            img_path (str): Path to image file.
        """
        self._queue.append(img_path)

    def save_queue(self):
        """Save queued files."""
        if not self._queue:
            return

        text = []
        for p in self._queue:
            if isinstance(p, unicode):
                p = p.encode('utf-8')
            text.append(p)
            logger.info('Queued for thumbnail generation : %r', p)

        logger.info('self.cachedir=%s', self.cachedir)

        text = b'\n'.join(text)
        with LockFile(self._queue_path):
            with atomic_writer(self._queue_path, 'ab') as fp:
                fp.write(b'{}\n'.format(text))

        self._queue = []

    @property
    def has_queue(self):
        """Whether any files are queued for thumbnail generation.

        Returns:
            bool: ``True`` if there's a queue.
        """
        return (os.path.exists(self._queue_path) and
                os.path.getsize(self._queue_path) > 0)

    def process_queue(self):
        """Generate thumbnails for queued files."""
        logger.info('process queue')

        if not self.has_queue:
            logger.info("Thumbnail queue empty")
            return

        queue = []
        with LockFile(self._queue_path):
            with open(self._queue_path) as fp:
                for line in fp:
                    line = line.strip()
                    if not line:
                        continue
                    self.download_image(line)
                    with atomic_writer(self._queue_path, 'wb') as fp:
                        pass
                        fp.write('')

    def download_image(self, img_path):
        h = hashlib.md5(img_path).hexdigest()
        thumb_path = os.path.join(self.cachedir, u'{}.png'.format(h))
        logger.info("Download - download_path=%s" % thumb_path)

        cmd = [
            '/usr/bin/curl',
            img_path,
            "-o", thumb_path,
        ]

        retcode = subprocess.call(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)

        if retcode:
            logger.info('download exited with %d : %s', retcode, img_path)
            return False
        return thumb_path


def main(wf):
    """Generate any thumbnails pending in the queue.

    Args:
        wf (Workflow): Current workflow instance.
    """
    logger.info("===main====")

    t = Thumbs(wf.datafile('thumbs'))
    t.process_queue()


if __name__ == '__main__':
    # logger.info("===ThumbsThumbsThumbsThumbsThumbsThumbsThumbs====")

    # wf = Workflow()
    # logger = wf.logger
    sys.exit(wf.run(main))
