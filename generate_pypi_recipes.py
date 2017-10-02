#!/usr/bin/env python3
#
# Copyright (C) 2017 Viktor Sjölind
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# SPDX-License-Identifier: MPL-2.0

import argparse
from datetime import date

import requests

DATA_FIELD_PYPI_PACKAGE_TAG = "name"

LABEL_PYPI_PACKAGE_TAG = "PYPI_PACKAGE"

DATA_FIELD_DEPENDENCIES = 'requires_dist'

LABEL_LICENSE = "LICENSE"
LABEL_HOMEPAGE= "HOMEPAGE"
LABEL_SUMMARY = "SUMMARY"
LABEL_DESCRIPTION = "DESCRIPTION"
LABEL_SOURCE_REVISION = "SRC_URI[md5sum]"

DATA_FIELD_LICENSE = "license"
DATA_FIELD_HOMEPAGE = "package_url"
DATA_FIELD_SUMMARY = "summary"
DATA_FIELD_DESCRIPTION = "summary"
DATA_FIELD_SOURCE_REVISION = 'md5_digest'
DATA_FIELD_RELEASE_TYPE = 'python_version'


def generate_summary(data):
    return generate_entry(LABEL_SUMMARY, DATA_FIELD_SUMMARY, data)


def generate_description(data):
    return generate_entry(LABEL_DESCRIPTION, DATA_FIELD_SUMMARY, data)


def generate_homepage(data):
    return generate_entry(LABEL_HOMEPAGE, DATA_FIELD_HOMEPAGE, data)


def generate_entry(recipe_heading, data_field, data, mandatory=False):
    if data_field in data:
        return "{} = \"{}\"\n".format(recipe_heading, data[data_field])
    elif mandatory:
        raise MandatoryEntryEmpty()
    else:
        return ""


def generate_license(data):
    return generate_entry(LABEL_LICENSE, DATA_FIELD_LICENSE, data, mandatory=True)


def generate_source_revision(release_data):
    return generate_entry(LABEL_SOURCE_REVISION, DATA_FIELD_SOURCE_REVISION, release_data, mandatory=True)


def is_source_release(release_data):
    if DATA_FIELD_RELEASE_TYPE in release_data:
        return release_data[DATA_FIELD_RELEASE_TYPE] == 'source'
    else:
        raise MissingDataField()


def parse_dependency(dependency_line):
    dependency_line = dependency_line.replace(";", "")
    return dependency_line.split(" ")[0]


def list_dependencies(package_data):
    if DATA_FIELD_DEPENDENCIES in package_data:
        return map(parse_dependency, package_data[DATA_FIELD_DEPENDENCIES])
    else:
        return []


def generate_rdepends(package_data):
    rdepends_entry = "RDEPENDS_${PN} = \"\\\n"
    for dependency in list_dependencies(package_data):
        rdepends_entry += "    ${PYTHON_PN}-%s \\\n" % dependency
    rdepends_entry += "\"\n"
    return rdepends_entry


def find_source_release_variant(release_variants):
    for release_variant in release_variants:
        if is_source_release(release_variant):
            return release_variant
    return None


def generate_pypi_package_tag(package_data):
    return generate_entry(LABEL_PYPI_PACKAGE_TAG, DATA_FIELD_PYPI_PACKAGE_TAG, package_data, mandatory=True)


class MissingDataField(Exception):
    def __init__(self):
        super()


class MandatoryEntryEmpty(Exception):
    def __init__(self):
        super()


def generate_recipe(package_data):
    latest_release = find_source_release_variant(package_data['urls'])

    return generate_summary(package_data['info'])            \
           + generate_description(package_data['info'])      \
           + generate_homepage(package_data['info'])         \
           + generate_license(package_data['info'])          \
           + "\n"                                            \
           + generate_source_revision(latest_release)        \
           + "\n"                                            \
           + generate_pypi_package_tag(package_data['info']) \
           + "\n"                                            \
           + generate_rdepends(package_data['info'])


def fetch_package_data(pypi_package_name):
    response = requests.get("https://pypi.python.org/pypi/{}/json".format(pypi_package_name))
    return response.json()


def generate_dependency_recipes(existing_recipies, dependencies):
    for dependency in dependencies:
        if dependency not in existing_recipies:
            generate_recipe_tree(dependency)


def generate_recipe_tree(pypi_package_name):
    package_data = fetch_package_data(pypi_package_name)
    recipe_content = generate_recipe(package_data)

    with open("python-{}.inc".format(pypi_package_name), "w") as f:
        f.write(recipe_content)

    release_version = package_data['info']['version']
    with open("python-{}_{}.bb".format(pypi_package_name, release_version), "w") as f:
        f.writelines(["inherit pypi setuptools\n",
                      "require python-{}.inc\n".format(pypi_package_name)])

    with open("python3-{}_{}.bb".format(pypi_package_name, release_version), "w") as f:
        f.writelines(["inherit pypi setuptools\n",
                      "require python-{}.inc\n".format(pypi_package_name)])

    dependencies = list_dependencies(package_data['info'])
    generate_dependency_recipes([], dependencies)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pypi_package",
                        help="The pypi package to create recipes for (including all of its dependencies)")
    args = parser.parse_args()

    generate_recipe_tree(args.pypi_package)
