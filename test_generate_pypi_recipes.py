#!/usr/bin/env python3
#
# Copyright (C) 2017 Viktor Sjölind
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# SPDX-License-Identifier: MPL-2.0

import unittest
from datetime import date

import generate_pypi_recipes


class MyTestCase(unittest.TestCase):


    def test_generate_summary(self):
        self.call_generate_function_with_data(generate_pypi_recipes.generate_summary,
                                              recipe_heading=generate_pypi_recipes.LABEL_SUMMARY,
                                              data_field=generate_pypi_recipes.DATA_FIELD_SUMMARY)
        self.call_non_mandatory_generate_function_without_data(generate_pypi_recipes.generate_summary)

    def test_generate_description(self):
        self.call_generate_function_with_data(generate_pypi_recipes.generate_description,
                                              recipe_heading=generate_pypi_recipes.LABEL_DESCRIPTION,
                                              data_field=generate_pypi_recipes.DATA_FIELD_DESCRIPTION)
        self.call_non_mandatory_generate_function_without_data(generate_pypi_recipes.generate_summary)

    def test_generate_homepage(self):
        self.call_generate_function_with_data(generate_pypi_recipes.generate_homepage,
                                              recipe_heading=generate_pypi_recipes.LABEL_HOMEPAGE,
                                              data_field=generate_pypi_recipes.DATA_FIELD_HOMEPAGE)
        self.call_non_mandatory_generate_function_without_data(generate_pypi_recipes.generate_homepage)

    def test_generate_license(self):
        self.call_generate_function_with_data(generate_pypi_recipes.generate_license,
                                              recipe_heading=generate_pypi_recipes.LABEL_LICENSE,
                                              data_field=generate_pypi_recipes.DATA_FIELD_LICENSE)
        self.call_mandatory_generate_function_without_data(generate_pypi_recipes.generate_license)

    def test_genereate_source_revision(self):
        self.call_generate_function_with_data(generate_pypi_recipes.generate_source_revision,
                                              recipe_heading=generate_pypi_recipes.LABEL_SOURCE_REVISION,
                                              data_field=generate_pypi_recipes.DATA_FIELD_SOURCE_REVISION)
        self.call_mandatory_generate_function_without_data(generate_pypi_recipes.generate_source_revision)

    def call_generate_function_with_data(self, fun, recipe_heading, data_field):
        data = {data_field: "GARBLE GARBLE"}
        self.assertEqual(fun(data), "{} = \"{}\"\n".format(recipe_heading, data[data_field]))

    def call_non_mandatory_generate_function_without_data(self, fun):
        self.assertEqual(fun({}), "")

    def call_mandatory_generate_function_without_data(self, fun):
        with self.assertRaises(generate_pypi_recipes.MandatoryEntryEmpty):
            fun({})

    def test_is_source_release(self):
        release_data = {generate_pypi_recipes.DATA_FIELD_RELEASE_TYPE: 'source'}
        self.assertEqual(generate_pypi_recipes.is_source_release(release_data), True)

    def test_is_source_release_wrong_type(self):
        release_data = {generate_pypi_recipes.DATA_FIELD_RELEASE_TYPE: 'sdist'}
        self.assertEqual(generate_pypi_recipes.is_source_release(release_data), False)

    def test_is_source_release_with_missing_data_field_raise_exception(self):
        with self.assertRaises(generate_pypi_recipes.MissingDataField):
            generate_pypi_recipes.is_source_release({})

    def test_list_dependencies_empty(self):
        dependency_list = []
        dependency_data = self.create_dependency_data(dependency_list)
        self.assertEqual(list(generate_pypi_recipes.list_dependencies(dependency_data)), dependency_list)

    def test_list_dependencies(self):
        dependency_list = ['foo; (!=1.5.7,>=1.5.6)']
        result_list = ['foo']
        dependency_data = self.create_dependency_data(dependency_list)
        self.assertEqual(list(generate_pypi_recipes.list_dependencies(dependency_data)), result_list)

    def create_dependency_data(self, dependency_list):
        return {generate_pypi_recipes.DATA_FIELD_DEPENDENCIES: dependency_list}

    def test_generate_rdepends(self):
        dependency_list = ['foo; (!=1.5.7,>=1.5.6)']
        dependency_data = self.create_dependency_data(dependency_list)
        self.assertEqual(generate_pypi_recipes.generate_rdepends(dependency_data),
                         "RDEPENDS_${PN} = \"\\\n    ${PYTHON_PN}-foo \\\n\"\n")

    def test_find_source_release_variant_empty(self):
        self.assertEqual(generate_pypi_recipes.find_source_release_variant([]), None)

    def test_find_source_release_variant(self):
        source_release = {generate_pypi_recipes.DATA_FIELD_RELEASE_TYPE: 'source'}
        other_release = {generate_pypi_recipes.DATA_FIELD_RELEASE_TYPE: 'sdist'}

        self.assertEqual(generate_pypi_recipes.find_source_release_variant([source_release, other_release]),
                         source_release)

    def test_generate_pypi_package_tag(self):
        self.call_generate_function_with_data(generate_pypi_recipes.generate_pypi_package_tag,
                                              recipe_heading=generate_pypi_recipes.LABEL_PYPI_PACKAGE_TAG,
                                              data_field=generate_pypi_recipes.DATA_FIELD_PYPI_PACKAGE_TAG)
        self.call_mandatory_generate_function_without_data(generate_pypi_recipes.generate_pypi_package_tag)

if __name__ == '__main__':
    unittest.main()
