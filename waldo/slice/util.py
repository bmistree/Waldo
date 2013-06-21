#!/usr/bin/env python

import json;


def toJsonPretty(dictOrArray):
    return json.dumps(dictOrArray,sort_keys=True, indent=4);

def fromJsonPretty(jsonStr):
    return json.loads(jsonStr);
