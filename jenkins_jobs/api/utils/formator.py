#!/usr/bin/env python
#-*- coding:UTF-8 -*-
import json
def gmsg(code, message, result=[], **kwags):
    data = dict(
        success = True,
        code = "%d"%code,
        msg = message
    )
    if code != 0:
        data = dict(
            success = False,
            code = "%d"%code,
            msg = message
        )

    if result:
        data['data'] = result
    data.update(kwags)
    return json.dumps(data)
