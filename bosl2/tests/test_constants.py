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

"""Tests for bosl2/constants.py: the Vec3 direction constants and their arithmetic."""

from bosl2.constants import (
    BACK,
    BOTTOM,
    CENTER,
    DOWN,
    FRONT,
    LEFT,
    RIGHT,
    TOP,
    UP,
    Vec3,
)


def test_constant_values():
    assert list(LEFT) == [-1, 0, 0]
    assert list(RIGHT) == [1, 0, 0]
    assert list(FRONT) == [0, -1, 0]
    assert list(BACK) == [0, 1, 0]
    assert list(TOP) == [0, 0, 1]
    assert list(BOTTOM) == [0, 0, -1]
    assert list(CENTER) == [0, 0, 0]


def test_aliases():
    assert UP is TOP
    assert DOWN is BOTTOM


def test_addition_combines_directions():
    assert list(TOP + LEFT) == [-1, 0, 1]
    assert list(TOP + FRONT + RIGHT) == [1, -1, 1]


def test_subtraction_and_negation():
    assert list(TOP - BOTTOM) == [0, 0, 2]
    assert list(-TOP) == [0, 0, -1]


def test_scalar_multiplication():
    assert list(TOP * 5) == [0, 0, 5]
    assert list(3 * RIGHT) == [3, 0, 0]


def test_result_is_vec3():
    assert isinstance(TOP + LEFT, Vec3)
    assert isinstance(TOP * 2, Vec3)


def test_is_a_list():
    assert isinstance(TOP, list)
    assert TOP == [0, 0, 1]
