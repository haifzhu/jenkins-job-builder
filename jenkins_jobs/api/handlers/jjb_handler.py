#!/usr/bin/env python
#-*- coding:UTF-8 -*-
import logging
import sys
import json
import tornado.web
from jenkins_jobs.api.utils.formator import gmsg
from jenkins_jobs.api.utils.entry import JenkinsEntry
import jenkins_jobs.utils as utils
import jenkins_jobs.builder as builder
import jenkins_jobs.parser as parser
import jenkins_jobs.registry as registry

logger = logging.getLogger(__name__)

class JJBEntryHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        try:
            self.write(gmsg(0, "数据获取成功", result=list(j['name'] for j in JenkinsEntry.get_instance().get_jobs())))
        except Exception as e:
            logger.error(e)
            self.write(gmsg(1, "数据获取失败"))
        finally:
            self.finish()

    @tornado.web.asynchronous
    def delete(self, *args, **kwargs):
        try:
            jobname = kwargs.get('name', None)
            if not jobname:
                self.write(gmsg(-1, "参数错误"))
                return

            JenkinsEntry.get_instance().delete_job(name=jobname)

            self.write(get_gmsg_from_result(result, okmessage="操作成功"))
        except Exception as e:
            logger.error(e)
            self.write(gmsg(1, "操作失败"))
        finally:
            self.finish()

    @tornado.web.asynchronous
    def post(self):
        try:
            param = self.request.body.decode('utf-8')
            data = json.loads(param)
            if not data.get("path") or not data.get("type"):
                self.write(gmsg(-1, "参数错误"))
                return

            path = data.get("path")
            type = data.get("type")

            jenkins_entry = JenkinsEntry()
            jenkins_entry.update_jobs(path, type)
            self.write(gmsg(0, "操作成功"))
        except Exception as e:
            logger.error(e)
            self.write(gmsg(1, "操作失败"))
        finally:
            self.finish()
