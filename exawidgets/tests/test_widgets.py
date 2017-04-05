# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Test Base Widgets Functionality
################################
"""
import os
import platform
from subprocess import check_call
from unittest import TestCase


prckws = {'shell': True} if platform.system().lower() == "windows" else {}
nbname = "test_widgets.ipynb"
cwd = os.path.dirname(os.path.abspath(__file__))
nbpath = os.path.join(cwd, nbname)
tmppath = os.path.join(cwd, "tmp")
htmlpath = os.path.join(cwd, nbname.replace(".ipynb", ".html"))


class TestBaseWidgets(TestCase):
    """Executes the `test_widgets.ipynb`."""
    def setUp(self):
        """Execute the notebook."""
        try:
            check_call(["jupyter", "nbconvert", "--exec", nbpath],
                       cwd=cwd, **prckws)
        except Exception as e:
            self.fail(msg=str(e))

    def test_value_check(self):
        """Check bidirectional communication."""
        try:
            with open(tmppath) as f:
                value = int(f.read())
            self.assertEqual(value, 42)
        except Exception as e:
            self.fail(msg=str(e))

    def tearDown(self):
        """Cleanup the generated file."""
        try:
            os.remove(tmppath)
            os.remove(htmlpath)
        except Exception as e:
            self.fail(msg=str(e))
