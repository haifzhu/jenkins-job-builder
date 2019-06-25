#!/usr/bin/env python
#-*- coding:UTF-8 -*-
import logging
import sys
import time
from jenkins_jobs.api.utils.config import JJBAPIConfig
from jenkins_jobs.builder import JenkinsManager
from jenkins_jobs.parser import YamlParser
from jenkins_jobs.registry import ModuleRegistry
from jenkins_jobs.xml_config import XmlJobGenerator
from jenkins_jobs.xml_config import XmlViewGenerator
from jenkins_jobs.errors import JenkinsJobsException
from settings import conf

logger = logging.getLogger(__name__)

class JenkinsEntry():
    def __init__(self):
        pass

    @staticmethod
    def get_instance():
        jjb_config = JJBAPIConfig(url=conf.JENKINS_URL,user=conf.JENKINS_USER,password=conf.JENKINS_PASSWORD)
        return JenkinsManager(jjb_config)

    def _generate_xmljobs(self, path, name=None):
        jjb_config = JJBAPIConfig(url=conf.JENKINS_URL,user=conf.JENKINS_USER,password=conf.JENKINS_PASSWORD)
        builder = JenkinsManager(jjb_config)

        logger.info("Updating jobs in {0} ({1})".format(
            path, name))
        orig = time.time()

        # Generate XML
        parser = YamlParser(jjb_config)
        registry = ModuleRegistry(jjb_config, builder.plugins_list)
        xml_job_generator = XmlJobGenerator(registry)
        xml_view_generator = XmlViewGenerator(registry)

        parser.load_files(path)
        registry.set_parser_data(parser.data)

        job_data_list, view_data_list = parser.expandYaml(
            registry, name)

        xml_jobs = xml_job_generator.generateXML(job_data_list)
        xml_views = xml_view_generator.generateXML(view_data_list)

        jobs = parser.jobs
        step = time.time()
        logging.debug('%d XML files generated in %ss',
                      len(jobs), str(step - orig))

        return builder, xml_jobs, xml_views

    def update_jobs(self, path, type, name=None, n_workers=2, delete_old=False):
        if n_workers < 0:
            raise JenkinsJobsException(
                'Number of workers must be equal or greater than 0')

        builder, xml_jobs, xml_views = self._generate_xmljobs(path, name)

        if type == 'jobs':
            jobs, num_updated_jobs = builder.update_jobs(
                xml_jobs, n_workers=n_workers)
            logger.info("Number of jobs updated: %d", num_updated_jobs)
        elif type == 'views':
            views, num_updated_views = builder.update_views(
                xml_views, n_workers=n_workers)
            logger.info("Number of views updated: %d", num_updated_views)
        else:
            jobs, num_updated_jobs = builder.update_jobs(
                xml_jobs, n_workers=n_workers)
            logger.info("Number of jobs updated: %d", num_updated_jobs)
            views, num_updated_views = builder.update_views(
                xml_views, n_workers=n_workers)
            logger.info("Number of views updated: %d", num_updated_views)

        keep_jobs = [job.name for job in xml_jobs]
        if delete_old:
            n = builder.delete_old_managed(keep=keep_jobs)
            logger.info("Number of jobs deleted: %d", n)
