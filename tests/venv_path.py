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

# LibFile: tests/venv_path.py
#    Put the project's OWN .venv ahead of everything else on sys.path.
#
#    The pure-Python tests import pybosl2 directly, and without this they get whatever the
#    ambient interpreter happens to find -- on this machine a separate pybosl2 dev checkout,
#    which is NOT the version the toolkit builds against. That made tests fail on symbols
#    that exist perfectly well in the pinned copy (catenary, hsl/hsv), which is worse than
#    useless: it reports problems the shipped code does not have, and would equally hide
#    real ones. The render tests never had this problem because render_app.py writes the
#    same path insert into every script it sends to the app.
#
#    Import this FIRST, before pybosl2:
#
#        import venv_path  # noqa: F401  -- pins pybosl2 to the project venv
#        from pybosl2 import Path2D
#
# FileGroup: Tests

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def site_packages() -> str | None:
    """The project venv's site-packages, or None when there is no venv."""
    hits = list(PROJECT_ROOT.glob(".venv/lib/*/site-packages"))
    return str(hits[0]) if hits else None


def install() -> str | None:
    """Put the project venv first on sys.path (idempotent). Returns the path used."""
    sp = site_packages()
    if sp and sys.path[:1] != [sp]:
        while sp in sys.path:
            sys.path.remove(sp)
        sys.path.insert(0, sp)
    return sp


install()
