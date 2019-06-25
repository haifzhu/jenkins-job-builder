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

class JenkinsEntry(JenkinsManager):
    def __init__(self, url=conf.JENKINS_URL,user=conf.JENKINS_USER,password=conf.JENKINS_PASSWORD):
        self.jjb_config = JJBAPIConfig(url=url, user=user, password=password)
        super().__init__(self.jjb_config)

    def get_instance(self):
        return JenkinsManager(self.jjb_config)

    def job_info(self, job_name):
        if self.is_job(job_name):
            return self.jenkins.get_job_info(job_name)
        logger.warning("Job {0} is not exists".format(job_name))
        return None

    def next_bn(self, job_name):
        job_info = self.job_info(job_name)
        if job_info:
            return job_info.get('nextBuildNumber')
        return None

    def build_job(self, job_name, parameter=None):
        next_bn = self.next_bn(job_name)
        if self.is_job(job_name):
            self.run_job(job_name, parameter)

        return (job_name, next_bn)

    def run_job(self, job_name, parameter):
        return self.jenkins.build_job(job_name, parameter)

    def console_output(self, job_name, build_num):
        return self.jenkins.get_build_console_output(job_name, build_num)

    def _generate_xmljobs(self, path, name=None):
        builder = JenkinsManager(self.jjb_config)

        logger.info("Updating jobs in {0} ({1})".format(
            path, name))
        orig = time.time()

        # Generate XML
        parser = YamlParser(self.jjb_config)
        registry = ModuleRegistry(self.jjb_config, builder.plugins_list)
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
