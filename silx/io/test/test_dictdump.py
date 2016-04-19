# coding: utf-8
#/*##########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
"""Tests for dicttoh5 module"""

__authors__ = ["P. Knobel"]
__license__ = "MIT"
__date__ = "19/04/2016"

import h5py
import numpy
import os
import tempfile
import unittest

from collections import defaultdict

from ..configdict import ConfigDict
from ..dictdump import dicttoh5, dicttojson, dicttoini, dump, load


def tree():
    """Tree data structure as a recursive nested dictionary"""
    return defaultdict(tree)


city_attrs = tree()
city_attrs["Europe"]["France"]["Grenoble"]["area"] = "18.44 km2"
city_attrs["Europe"]["France"]["Grenoble"]["inhabitants"] = 160215
city_attrs["Europe"]["France"]["Grenoble"]["coordinates"] = [45.1830, 5.7196]
city_attrs["Europe"]["France"]["Tourcoing"]["area"]


class TestDictToH5(unittest.TestCase):
    def setUp(self):
        fd, self.h5_fname = tempfile.mkstemp(text=False)
        # Close and delete (we just want the name)
        os.close(fd)
        os.unlink(self.h5_fname)

    def tearDown(self):
        os.unlink(self.h5_fname)

    def testH5CityAttrs(self):
        filters = {'compression': "gzip", 'shuffle': True,
                   'fletcher32': True}
        dicttoh5(city_attrs, self.h5_fname, h5path='/city attributes',
                 mode="w", create_dataset_args=filters)

        h5f = h5py.File(self.h5_fname)

        self.assertIn("Tourcoing/area", h5f["/city attributes/Europe/France"])
        ds = h5f["/city attributes/Europe/France/Grenoble/inhabitants"]
        self.assertEqual(ds[...], 160215)

        # filters only apply to datasets that are not scalars (shape != () )
        ds = h5f["/city attributes/Europe/France/Grenoble/coordinates"]
        self.assertEqual(ds.compression, "gzip")
        self.assertTrue(ds.fletcher32)
        self.assertTrue(ds.shuffle)

        h5f.close()

        ddict = load(self.h5_fname, fmat="hdf5")
        self.assertAlmostEqual(
                min(ddict["city attributes"]["Europe"]["France"]["Grenoble"]["coordinates"]),
                5.7196)


class TestDictToJson(unittest.TestCase):
    def setUp(self):
        self.dir_path = tempfile.mkdtemp()
        self.json_fname = os.path.join(self.dir_path, "cityattrs.json")

    def tearDown(self):
        os.unlink(self.json_fname)
        os.rmdir(self.dir_path)

    def testJsonCityAttrs(self):
        self.json_fname = os.path.join(self.dir_path, "cityattrs.json")
        dicttojson(city_attrs, self.json_fname, indent=3)

        with open(self.json_fname, "r") as f:
            json_content = f.read()
            self.assertIn('"inhabitants": 160215', json_content)


class TestDictToIni(unittest.TestCase):
    def setUp(self):
        self.dir_path = tempfile.mkdtemp()
        self.ini_fname = os.path.join(self.dir_path, "test.ini")

    def tearDown(self):
        os.unlink(self.ini_fname)
        os.rmdir(self.dir_path)

    def testConfigDictIO(self):
        testdict = {
            'simple_types': {
                'float': 1.0,
                'int': 1,
                'string': 'Hello World',
            },
            'containers': {
                'list': [-1, 'string', 3.0, False],
                'array': numpy.array([1.0, 2.0, 3.0]),
                'dict': {
                    'key1': 'Hello World',
                    'key2': 2.0,
                }
            }
        }

        dump(testdict, self.ini_fname, fmat="ini")

        #read the data back
        readinstance = ConfigDict()
        readinstance.read(self.ini_fname)

        testdictkeys = list(testdict.keys())
        readkeys = list(readinstance.keys())

        self.assertTrue(len(readkeys) == len(testdictkeys),
                        "Number of read keys not equal")

        for key in testdict["simple_types"]:
            original = testdict['simple_types'][key]
            read = readinstance['simple_types'][key]
            self.assertEqual(read, original,
                             "Read <%s> instead of <%s>" % (read, original))

        for key in testdict["containers"]:
            original = testdict["containers"][key]
            read = readinstance["containers"][key]
            if key == 'array':
                self.assertEqual(read.all(), original.all(),
                            "Read <%s> instead of <%s>" % (read, original))
            else:
                self.assertEqual(read, original, 
                                 "Read <%s> instead of <%s>" % (read, original))



def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestDictToIni))
    test_suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestDictToH5))
    test_suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestDictToJson))
    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")