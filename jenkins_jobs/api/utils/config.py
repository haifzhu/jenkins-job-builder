#!/usr/bin/env python
import logging
from jenkins_jobs.config import JJBConfig

__all__ = [
    "JJBAPIConfig"
]

logger = logging.getLogger(__name__)


class JJBAPIConfig(JJBConfig):
    def __init__(self, url, user, password, timeout=1):
        self.jenkins = {
            "url": url,
            "user": user,
            "password": password,
            "timeout": timeout
        }

        self.builder = {
            "ignore_cache": False,
            "flush_cache": False,
            "print_job_urls": False,
            "update": "all",
            "plugins_info": []
        }

        self.yamlparser = {
            "keep_descriptions": False,
            "allow_duplicates": False,
            "allow_empty_variables": False,
            "retain_anchors": False,
            "include_path": ['.'],
            "retain_anchors": False,
        }
