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

# LibFile: bosl2/docs/_ext/stl_viewer.py
#    Sphinx extension providing an ``.. stl:: <uri>`` directive that embeds an INTERACTIVE 3-D
#    viewer (rotate / pan / zoom) for an STL mesh, the same idea as the PyPI ``sphinxstl``
#    package's directive -- but self-contained and working on current Sphinx.
#
#    The real ``sphinxstl`` (0.1.1) cannot be used here: it calls the ``app.add_javascript()``
#    API that Sphinx removed in 4.0, and its wheel ships without the thingiview.js/three.min.js
#    assets it depends on. This drop-in registers the same ``stl`` directive name, but renders
#    with three.js (loaded as ES modules from a CDN via esm.sh, so no importmap or vendored
#    bundle is needed) and needs no build-finished asset copying.
#
#    ``bosl2/docs/_ext/bosl2_example.py`` reuses :func:`stl_viewer_html` to show an interactive
#    viewer for each rendered example's exported STL, right beside its source and a download link.
#
# FileGroup: bosl2

from __future__ import annotations

from uuid import uuid4

from docutils import nodes
from docutils.parsers.rst import Directive, directives

# three.js pulled from esm.sh, which rewrites the addon modules' bare ``import ... from "three"``
# to the matching pinned build, so STLLoader/OrbitControls share the same THREE instance without
# needing a page-level importmap.
_THREE = "https://esm.sh/three@0.160.0"

_TEMPLATE = """
<div class="stl-viewer" id="{vid}" style="width:{width};height:{height};border:1px solid #ddd;\
border-radius:4px;background:{background};touch-action:none"></div>
<script type="module">
import * as THREE from "{three}";
import {{ STLLoader }} from "{three}/examples/jsm/loaders/STLLoader.js";
import {{ OrbitControls }} from "{three}/examples/jsm/controls/OrbitControls.js";

const el = document.getElementById("{vid}");
const scene = new THREE.Scene();
scene.background = new THREE.Color("{background}");
const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 1e6);
camera.up.set(0, 0, 1);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
el.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
const key = new THREE.DirectionalLight(0xffffff, 0.85); key.position.set(1, 0.6, 1); scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff, 0.4); fill.position.set(-1, -0.8, 0.5); scene.add(fill);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

function resize() {{
  const w = el.clientWidth, h = el.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / Math.max(1, h);
  camera.updateProjectionMatrix();
}}

new STLLoader().load("{uri}", function (geo) {{
  geo.computeVertexNormals();
  geo.computeBoundingBox();
  const center = new THREE.Vector3(); geo.boundingBox.getCenter(center);
  const size = new THREE.Vector3(); geo.boundingBox.getSize(size);
  geo.translate(-center.x, -center.y, -center.z);
  const mesh = new THREE.Mesh(geo, new THREE.MeshPhongMaterial({{
    color: "{color}", specular: 0x222222, shininess: 25, flatShading: false,
  }}));
  scene.add(mesh);
  const r = Math.max(size.x, size.y, size.z) || 1;
  camera.position.set(r * 1.3, -r * 1.7, r * 1.1);
  controls.target.set(0, 0, 0);
  resize();
  (function animate() {{ requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }})();
}}, undefined, function (err) {{
  el.innerHTML = '<p style="padding:1em;color:#a00">Could not load STL (serve the docs over HTTP to view).</p>';
}});
window.addEventListener("resize", resize);
</script>
"""


def stl_viewer_html(uri: str, width: str = "100%", height: str = "360px",
                    color: str = "#4a90d9", background: str = "#f7f7f9") -> str:
    """The raw HTML embedding an interactive three.js viewer for the STL at *uri*."""
    return _TEMPLATE.format(vid="stlviewer-" + uuid4().hex, uri=uri, three=_THREE,
                            width=width, height=height, color=color, background=background)


class STLDirective(Directive):
    """``.. stl:: <uri>`` -- embed an interactive 3-D viewer for an STL file (sphinxstl-compatible)."""

    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "color": directives.unchanged,
        "background": directives.unchanged,
        "width": directives.unchanged,
        "height": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        html = stl_viewer_html(
            self.arguments[0],
            width=self.options.get("width", "100%"),
            height=self.options.get("height", "360px"),
            color=self.options.get("color", "#4a90d9"),
            background=self.options.get("background", "#f7f7f9"),
        )
        return [nodes.raw("", html, format="html")]


def setup(app) -> dict:
    app.add_directive("stl", STLDirective)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
