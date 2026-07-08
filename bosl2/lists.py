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

# LibFile: bosl2/lists.py
#    Pure-Python port of the pieces of BOSL2's lists.scad (plus column()
#    from linalg.scad) that bosl2/paths.py depends on. No osuse()/BOSL2
#    runtime dependency -- this is plain Python.
#
# FileSummary: General list-manipulation helpers (BOSL2 lists.scad).
# FileGroup: BOSL2


def select(lst: list, start: int | list[int], end: int | None = None) -> object:
    """Circular list indexing/slicing.

    select(lst, i) returns lst[i], wrapping i modulo len(lst).
    select(lst, [i, j, ...]) returns [lst[i], lst[j], ...], each wrapped.
    select(lst, s, e) returns the circular slice lst[s..e] inclusive, wrapping
    around the end of the list if s > e.
    """
    n = len(lst)
    if n == 0:
        return []
    if end is None:
        if isinstance(start, (list, tuple)):
            return [lst[i % n] for i in start]
        return lst[start % n]
    s = start % n
    e = end % n
    if s <= e:
        return [lst[i] for i in range(s, e + 1)]
    return [lst[i] for i in range(s, n)] + [lst[i] for i in range(0, e + 1)]


def pair(lst: list, wrap: bool = False) -> list[tuple]:
    """List of consecutive (lst[i], lst[i+1]) pairs; if wrap, also (last, first)."""
    length = len(lst) - 1
    if length < 1:
        return []
    out = [(lst[i], lst[i + 1]) for i in range(length)]
    if wrap:
        out.append((lst[length], lst[0]))
    return out


def list_set(lst: list, indices: int | list[int], values, dflt=0, minlen: int = 0) -> list:
    """Return a copy of *lst* with entries at *indices* replaced by *values*.

    *indices*/*values* may each be a single index/value, or matching lists.
    """
    if not isinstance(indices, (list, tuple)):
        if isinstance(indices, int) and indices < len(lst):
            out = [values if i == indices else lst[i] for i in range(len(lst))]
            out.extend([dflt] * max(0, minlen - len(lst)))
            return out
        return list_set(lst, [indices], [values], dflt)
    if len(indices) == 0 and len(values) == 0:
        return list(lst) + [dflt] * max(0, minlen - len(lst))
    assert len(values) == len(indices), "Index list and value list must have the same length"
    lookup = dict(zip(indices, values))
    midx = max(len(lst) - 1, max(indices))
    out = []
    for i in range(midx + 1):
        if i in lookup:
            out.append(lookup[i])
        elif i < len(lst):
            out.append(lst[i])
        else:
            out.append(dflt)
    out.extend([dflt] * max(0, minlen - max(len(lst), max(indices) + 1)))
    return out


def list_head(lst: list, to: int = -2) -> list:
    """Return the elements of *lst* up to and including index *to*."""
    if to < 0:
        return lst[: len(lst) + to + 1]
    if to < len(lst):
        return lst[: to + 1]
    return list(lst)


def list_tail(lst: list, frm: int = 1) -> list:
    """Return the elements of *lst* starting at index *frm* (may be negative)."""
    if frm < 0:
        frm = frm + len(lst)
    if frm < 0:
        return list(lst)
    return lst[frm:]


def slice(lst: list, start: int = 0, end: int = -1) -> list:
    """Return lst[start..end] inclusive; negative indices count from the end."""
    if not lst:
        return []
    length = len(lst)
    s = max(0, min(length - 1, start + (length if start < 0 else 0)))
    e = max(0, min(length - 1, end + (length if end < 0 else 0)))
    if e < s:
        return []
    return lst[s : e + 1]


def repeat(val, n: int) -> list:
    """Return a list containing *val* repeated *n* times."""
    return [val for _ in range(n)]


def column(matrix: list[list], i: int) -> list:
    """Extract column *i* from a list of rows."""
    return [row[i] for row in matrix]
