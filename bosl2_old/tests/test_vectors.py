# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Tests for bosl2/vectors.py: is_vector(), add_scalar(), unit()."""

import math

import numpy as np
import pytest

from bosl2.vectors import add_scalar, is_vector, unit


def test_is_vector_basic():
    assert is_vector([1, 2, 3])
    assert not is_vector(5)
    assert not is_vector("abc")


def test_is_vector_length():
    assert is_vector([1, 2, 3], length=3)
    assert not is_vector([1, 2, 3], length=2)


def test_is_vector_zero_flag():
    assert is_vector([0, 0, 0], zero=True)
    assert not is_vector([0, 0, 1], zero=True)
    assert is_vector([0, 0, 1], zero=False)
    assert not is_vector([0, 0, 0], zero=False)


def test_add_scalar():
    np.testing.assert_allclose(add_scalar([1, 2, 3], 10), [11, 12, 13])


def test_unit_normalizes():
    np.testing.assert_allclose(unit([3, 0, 0]), [1, 0, 0])
    np.testing.assert_allclose(unit([0, 5]), [0, 1])


def test_unit_length_is_one():
    v = unit([1, 2, 2])
    assert math.isclose(float(np.linalg.norm(v)), 1.0)


def test_unit_zero_with_default_error_value():
    # a supplied `error` value is returned for a zero-length vector instead of dividing by zero
    np.testing.assert_allclose(unit([0, 0], [9, 9]), [9, 9])


def test_unit_zero_without_error_raises():
    with pytest.raises(Exception):
        unit([0, 0, 0])
