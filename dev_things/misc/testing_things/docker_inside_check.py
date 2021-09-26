import os


def is_docker():
    path = '/proc/self/cgroup'
    return (os.path.exists('/.dockerenv') or os.path.isfile(path) and any('docker' in line for line in open(path)))


print(is_docker())
