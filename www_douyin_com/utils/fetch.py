#!/usr/bin/env python 
# coding:utf-8

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from retrying import retry

from www_douyin_com.config import (DEFALUT_REQ_TIMEOUT, MAX_RETRY_REQ_TIMES, RETRY_RANDON_MAX_WAIT,
                                   RETRY_RANDON_MIN_WAIT)

from www_douyin_com.utils.proxy import grab_proxy


def need_retry(exception):
    result = isinstance(exception, (requests.ConnectionError, requests.ReadTimeout))
    if result:
        print("Exception", type(exception), "occurred retrying...")
    return result


def fetch(url, **kwargs):

    @retry(stop_max_attempt_number=MAX_RETRY_REQ_TIMES, wait_random_min=RETRY_RANDON_MIN_WAIT,
           wait_random_max=RETRY_RANDON_MAX_WAIT, retry_on_exception=need_retry)
    def _fetch(url, **kwargs):
        kwargs.update({"verify": False})
        kwargs.update({"timeout": kwargs.get("timeout") or DEFALUT_REQ_TIMEOUT})
        if kwargs.get("USE_PROXY"):
            proxy = grab_proxy()
            kwargs.update({"proxies": {"http:": proxy, "https:": proxy.replace("http", "https")}})
        if kwargs.get("method") in ["post", "POST"]:
            form_data = kwargs.get("data") or kwargs.get("json")
            if not form_data:
                raise requests.RequestException("post method need form data, but got {}".format(form_data))
            kwargs.pop("method", None)
            response = requests.post(url, **kwargs)
        else:
            response = requests.get(url, **kwargs)
        if response.status_code != 200:
            raise requests.ConnectionError("request status code should be 200! but got {}".format(response.status_code))
        return response

    try:
        result = _fetch(url, **kwargs)
        return result
    except (requests.ConnectionError, requests.ReadTimeout):
        return {}
