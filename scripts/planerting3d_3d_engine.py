#!/usr/bin/env python3
"""
Planerting3d 3D Spatial Engine & Explorer Builder (v1.0)
========================================================
Compiles the canonical architecture catalog into a self-contained 3D web
application (Three.js/WebGL): 'planerting3d_explorer.html'.
"""

import os
import sys
import json
import argparse

def build_standalone_html(arch_json_path: str, out_html_path: str):
    with open(arch_json_path, 'r', encoding='utf-8') as f:
        arch_data = json.load(f)

    nodes_json_str = json.dumps(arch_data.get("components", []), ensure_ascii=False)
    conns_json_str = json.dumps(arch_data.get("connections", []), ensure_ascii=False)
    layers_json_str = json.dumps(arch_data.get("layers", []), ensure_ascii=False)
    meta_json_str = json.dumps(arch_data.get("meta", {}), ensure_ascii=False)

    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenGraphify — 3D Code Graph Explorer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #06080d;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
        }
        #canvas-container {
            width: 100vw;
            height: 100vh;
            position: absolute;
            top: 0;
            left: 0;
        }
        #hud {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 10;
            background: rgba(13, 17, 23, 0.92);
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 20px;
            width: 360px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }
        .brand-badge {
            background: linear-gradient(135deg, #58a6ff, #bc8cff);
            color: #0d1117;
            font-size: 11px;
            font-weight: 900;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }
        h1 {
            font-size: 18px;
            color: #58a6ff;
            font-weight: 700;
            letter-spacing: -0.3px;
        }
        p.subtitle {
            font-size: 12px;
            color: #8b949e;
            margin-bottom: 16px;
            line-height: 1.4;
        }
        .metric-card {
            background: #161b22;
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 14px;
            border: 1px solid #21262d;
        }
        .metric-row {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            padding: 4px 0;
            border-bottom: 1px solid #21262d;
        }
        .metric-row:last-child { border-bottom: none; }
        .metric-label { color: #8b949e; }
        .metric-val { color: #7ee787; font-weight: 600; font-family: monospace; }
        .metric-alert { color: #ff7b72; font-weight: 700; }
        
        .search-box {
            width: 100%;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 8px 12px;
            color: #fff;
            font-size: 12px;
            margin-bottom: 10px;
            outline: none;
        }
        .search-box:focus { border-color: #58a6ff; }
        
        .layer-legend {
            display: flex;
            flex-direction: column;
            gap: 6px;
            font-size: 11px;
            margin-top: 8px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            padding: 2px 4px;
            border-radius: 4px;
            transition: background 0.2s;
        }
        .legend-item:hover { background: #21262d; }
        .legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        
        #inspector {
            position: absolute;
            bottom: 20px;
            right: 20px;
            z-index: 10;
            background: rgba(13, 17, 23, 0.95);
            border: 1px solid #58a6ff;
            border-radius: 10px;
            padding: 18px;
            width: 420px;
            max-height: 520px;
            overflow-y: auto;
            backdrop-filter: blur(14px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7);
            display: none;
        }
        #inspector h2 {
            font-size: 15px;
            color: #58a6ff;
            margin-bottom: 6px;
            word-break: break-all;
        }
        #inspector .file-path {
            font-size: 11px;
            color: #8b949e;
            font-family: monospace;
            margin-bottom: 12px;
            border-bottom: 1px solid #30363d;
            padding-bottom: 6px;
        }
        .badge-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin: 8px 0 12px 0;
        }
        .badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
        }
        .badge-layer { background: #21262d; color: #58a6ff; border: 1px solid #30363d; }
        .badge-fanin { background: #1f6feb22; color: #79c0ff; border: 1px solid #1f6feb; }
        .section-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #8b949e;
            margin: 10px 0 4px 0;
            font-weight: 700;
        }
        .symbol-tag {
            display: inline-block;
            background: #161b22;
            color: #7ee787;
            font-family: monospace;
            font-size: 11px;
            padding: 2px 6px;
            border-radius: 4px;
            margin: 2px 3px 2px 0;
            border: 1px solid #30363d;
        }
        .close-btn {
            position: absolute;
            top: 14px;
            right: 14px;
            background: none;
            border: none;
            color: #8b949e;
            font-size: 16px;
            cursor: pointer;
        }
        .close-btn:hover { color: #fff; }
    </style>
    <script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
    <script src="https://unpkg.com/three@0.160.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="hud">
        <div class="brand">
            <span class="brand-badge">Planerting3d</span>
            <h1>Archify 3D Engine</h1>
        </div>
        <p class="subtitle">Deterministic AST-based code topology and architecture exploration.</p>

        <div class="metric-card">
            <div class="metric-row">
                <span class="metric-label">Components (AST)</span>
                <span class="metric-val" id="metric-components">0</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Resolved edges</span>
                <span class="metric-val" id="metric-connections">0</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Model-token cost</span>
                <span class="metric-val" style="color: #58a6ff;">0 (D*)</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Cataloger mode</span>
                <span class="metric-val metric-alert">Deterministic</span>
            </div>
        </div>

        <input type="text" id="search" class="search-box" placeholder="Search class, method, or file...">

        <div class="layer-legend" id="legend"></div>
    </div>

    <div id="inspector">
        <button class="close-btn" onclick="closeInspector()">×</button>
        <h2 id="insp-label">Component</h2>
        <div class="file-path" id="insp-file">path/to/file</div>
        <div class="badge-list" id="insp-badges"></div>

        <div class="section-title">Classes & interfaces (AST)</div>
        <div id="insp-classes"></div>

        <div class="section-title">Functions & hooks (AST)</div>
        <div id="insp-functions"></div>

    </div>

    <script>
        const nodesData = __NODES_JSON__;
        const connsData = __CONNS_JSON__;
        const layersData = __LAYERS_JSON__;
        const metaData = __META_JSON__;

        document.getElementById('metric-components').innerText = nodesData.length;
        document.getElementById('metric-connections').innerText = connsData.length;
        
        const legendContainer = document.getElementById('legend');
        const layerColorMap = {};
        layersData.forEach(l => {
            layerColorMap[l.id] = l.color;
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = '<span class="legend-dot" style="background: ' + l.color + ';"></span><span>' + l.name + '</span>';
            legendContainer.appendChild(item);
        });

        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x06080d, 0.002);
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 3000);
        camera.position.set(0, 80, 220);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambientLight);
        const pointLight = new THREE.PointLight(0x58a6ff, 2.0, 1500);
        pointLight.position.set(0, 150, 100);
        scene.add(pointLight);

        const grid = new THREE.GridHelper(600, 30, 0x21262d, 0x11161d);
        grid.position.y = -60;
        scene.add(grid);

        const nodeMeshes = [];
        const nodeMap = {};
        const sphereGeo = new THREE.SphereGeometry(5.0, 24, 24);

        nodesData.forEach(node => {
            const hexStr = layerColorMap[node.layer_id] ? layerColorMap[node.layer_id].replace('#', '0x') : '0x58a6ff';
            const color = parseInt(hexStr);
            const mat = new THREE.MeshStandardMaterial({
                color: color,
                emissive: color,
                emissiveIntensity: 0.25,
                roughness: 0.2,
                metalness: 0.8
            });
            const mesh = new THREE.Mesh(sphereGeo, mat);
            mesh.position.set(node.x, node.y, node.z);
            mesh.userData = node;
            scene.add(mesh);
            nodeMeshes.push(mesh);
            nodeMap[node.id] = mesh;
        });

        const lineMat = new THREE.LineBasicMaterial({ color: 0x388bfd, transparent: true, opacity: 0.35 });
        connsData.forEach(conn => {
            const src = nodeMap[conn.from];
            const tgt = nodeMap[conn.to];
            if (src && tgt) {
                const geo = new THREE.BufferGeometry().setFromPoints([src.position, tgt.position]);
                const line = new THREE.Line(geo, lineMat);
                scene.add(line);
            }
        });

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        window.addEventListener('click', (e) => {
            if (e.target.closest('#hud') || e.target.closest('#inspector')) return;
            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(nodeMeshes);
            if (intersects.length > 0) {
                showInspector(intersects[0].object.userData);
            }
        });

        function showInspector(node) {
            const insp = document.getElementById('inspector');
            insp.style.display = 'block';
            document.getElementById('insp-label').innerText = node.label;
            document.getElementById('insp-file').innerText = node.file;

            const badges = document.getElementById('insp-badges');
            badges.innerHTML = '<span class="badge badge-layer">' + node.layer_id + '</span>' +
                               '<span class="badge badge-fanin">Fan-in: ' + (node.fan_in || 0) + '</span>' +
                               '';

            const classesBox = document.getElementById('insp-classes');
            classesBox.innerHTML = node.classes && node.classes.length > 0 
                ? node.classes.map(c => '<span class="symbol-tag">' + c + '</span>').join('') 
                : '<span style="color: #6e7681; font-size: 11px;">No classes</span>';

            const funcsBox = document.getElementById('insp-functions');
            funcsBox.innerHTML = node.functions && node.functions.length > 0 
                ? node.functions.map(f => '<span class="symbol-tag">' + f + '</span>').join('') 
                : '<span style="color: #6e7681; font-size: 11px;">No functions</span>';
        }

        function closeInspector() {
            document.getElementById('inspector').style.display = 'none';
        }

        document.getElementById('search').addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase().trim();
            nodeMeshes.forEach(mesh => {
                const d = mesh.userData;
                const match = !q || d.label.toLowerCase().includes(q) || 
                              (d.classes && d.classes.some(c => c.toLowerCase().includes(q))) ||
                              (d.functions && d.functions.some(f => f.toLowerCase().includes(q)));
                mesh.material.opacity = match ? 1.0 : 0.15;
                mesh.material.transparent = !match;
            });
        });

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>"""

    final_html = template.replace("__NODES_JSON__", nodes_json_str)
    final_html = final_html.replace("__CONNS_JSON__", conns_json_str)
    final_html = final_html.replace("__LAYERS_JSON__", layers_json_str)
    final_html = final_html.replace("__META_JSON__", meta_json_str)

    with open(out_html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"[+] OpenGraphify 3D Explorer generated successfully: {out_html_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenGraphify 3D explorer compiler")
    parser.add_argument("--architecture", default="planerting3d.architecture.json")
    parser.add_argument("--output", default="planerting3d_explorer.html")
    args = parser.parse_args()
    arch_file = os.path.abspath(args.architecture)
    out_html = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out_html) or ".", exist_ok=True)
    build_standalone_html(arch_file, out_html)
