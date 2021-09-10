#!/bin/env python3

import sys
import pprint
import json

import botocove
import botocore
import boto3

import awscli.clidriver


class OrgSession(object):

    def __init__(self, *args, **kwargs):

        self._session = botocore.session.Session(*args, **kwargs)
    

    def create_client(self, *args, **kwargs):

        return OrgClient(self, *args, **kwargs)


    def __getattr__(self, name):
        
        return getattr(self._session, name)


class OrgClient(object):

    def __init__(self, session, *args, **kwargs):

        self._session = session
        self._client = session._session.create_client(*args, **kwargs)
        self._methods = self._client.meta.method_to_api_mapping
        self._args = args
        self._kwargs = kwargs


    def __getattr__(self, name):

        if name in self._methods:
            return self._dispatch(name)
        
        return getattr(self._client, name)
    

    def _dispatch(self, method):

        @botocove.cove
        def call_client_method(session, *args, **kwargs):

            c = session.client(*self._args, **self._kwargs)
            result = c.__getattribute__(method)(*args, **kwargs)
            return result

        return call_client_method


def climain():

    return create_clidriver().main()


def create_clidriver():
    session = OrgSession()
    awscli.plugin.load_plugins(
        session.full_config.get('plugins', {}),
        event_hooks=session.get_component('event_emitter')
    )
    driver = awscli.clidriver.CLIDriver(session=session)
    return driver


def simplemain():

    _, service_name, method_name = sys.argv
    api = OrgSession().create_client(service_name).__getattr__(method_name)
    result = api()
    print(json.dumps(result))


if __name__ == "__main__":
    simplemain()
