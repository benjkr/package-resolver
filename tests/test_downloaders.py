import random
import string
from logging import getLogger
from typing import List

import all_package_resolver.downloaders.lang as langs
import all_package_resolver.downloaders.os as os

# from mock import patch


def get_random_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def test_langs():
    classes: List[langs.LangDownloader] = [langs.NodeDownloader, langs.PythonDownloader]

    logger = getLogger(__name__)
    package = get_random_string(8)
    out_dir = get_random_string(8)
    version = get_random_string(8)
    for cls in classes:
        instance = cls(logger, package, out_dir, version)
        assert isinstance(instance, langs.LangDownloader)


def test_os():
    classes: List[os.OsDownloader] = [os.AlpineDownloader, os.CentosDownloader, os.UbuntuDownloader]

    logger = getLogger(__name__)
    package = get_random_string(8)
    out_dir = get_random_string(8)
    for cls in classes:
        instance = cls(logger, package, out_dir)
        assert isinstance(instance, os.OsDownloader)
