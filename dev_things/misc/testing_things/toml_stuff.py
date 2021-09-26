from pprint import pprint
import os
import toml
# import pytoml as toml


def stripper(data):
    new_data = {}
    for k, v in data.items():
        if isinstance(v, dict):
            v = stripper(v)
        if not v in (u'', None, {}, []):
            new_data[k] = v
    return new_data


def clean_empty(d):
    if isinstance(d, dict):
        return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}
    if isinstance(d, list):
        return [v for v in map(clean_empty, d) if v]
    return d


data = {
    "target": {
        "ip": "xx.xx.xx.xx",
        "os": {
            "os": "win 10",
            "Arch": "x64",
            "empty": {}
        },
        "ports": {
            "ports": ["1", "2"],
            "1": {
                "service": {
                    "xxx": "blah"
                },
                "ver": "5.9",
                "test": [{}, {}, {
                    "yo": "testing"
                }]
            }
        },
        "empty": {},
        "testing2": [{}, {}, {"cool", "test"}]
    }
}

# data = {
#     'root': [
#     {"empty": {}},
#     {
#         "_class": "hudson.model.AllView",
#         "name": "all",
#         "url": "http://localhost:8080/",
#         "empty": []
#     },
#     {
#         "_class": "hudson.model.FreeStyleProject",
#         "color": "blue",
#         "name": "testing",
#         "url": "http://localhost:8080/job/testing/"
#     }
# ]
# }
pprint(data)

# data = stripper(data)
data = clean_empty(data)
pprint(data)

toml_string = toml.dumps(data)
print(toml_string)

# EMPTY VALUES IN LIST DICT

# Python3 code to demonstrate working of
# Remove None value types in dictionaries list
# Using list comprehension

# initializing list
test_list = [{'gfg': 4, 'is': '', 'best': []}, {'I': {}, 'like': 5, 'gfg': 0}]

# printing original list
print("The original list is : " + str(test_list))

# Remove None value types in dictionaries list
# Using list comprehension
res = [ele for ele in ({key: val for key, val in sub.items() if val} for sub in test_list) if ele]

# printing result
print("The filtered list : " + str(res))
