#!/usr/bin/env python3
"""One-shot integrity gate for the Shelf design-repo.

Usage:
  python3 extraction/verify_all.py [--evidence-root DIR]

Checks (FAIL = exit 1, WARN = reported only):
  json-parse, schema (Draft-07 meta + example), semantic (example: 0 errors),
  allowlist parity (ids <-> contract files, node/page/motion properties <-> schema,
  templates, asset roles, generation policies), pinned asset-role policies,
  allowlistVersion parity, manifest counts recomputed from disk, entryPoints inside
  the package, no absolute local paths, citation validity (path + line range +
  quoted substring), graph <-> validator rule-id parity, route coverage 1:1,
  token catalog/policy/theme/alias parity, schema <-> section-contract parity,
  x-maxWords on every free-text field, README count parity, ia.json parity (WARN
  if absent).

Citations: every {"cite": "path:a[-b]", "quote": "..."} object anywhere in the
repo resolves against the evidence root (default: the folder containing
design-repo/). If that root has no CLONE_SPEC.md (standalone delivery), citation
and ia.json checks degrade to WARN. extraction/prove_drift.py proves the drift
checks actually fail on injected drift.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "schema"))

PINNED = {  # independent copy: drift in assets/asset-roles.json must be caught here
    "brand.logo-mark": "must-not-reproduce-real-brand",
    "brand.app-icons": "must-not-reproduce-real-brand",
    "icon.third-party-brand": "must-not-reproduce-real-brand",
    "mockup.thumbnail-color-block": "css-color-block-only",
    "form.waitlist-endpoint": "must-not-reuse-live-endpoint",
}
ABS_PATTERNS = [re.compile(p) for p in (r"/" + "Users" + r"/", r"/" + "home" + r"/[a-z]", r"[A-Z]:\\\\" + "Users", r"/private/" + "tmp", r"/" + "tmp/claude")]

FAILS, WARNS = [], []


def fail(check, msg):
    FAILS.append((check, msg))


def warn(check, msg):
    WARNS.append((check, msg))


def rel(*p):
    return os.path.join(REPO, *p)


def load(*p):
    with open(rel(*p), encoding="utf-8") as f:
        return json.load(f)


def repo_files():
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if fn == ".DS_Store" or fn.endswith(".pyc"):
                continue
            out.append(os.path.relpath(os.path.join(root, fn), REPO))
    return sorted(out)


def leaves(d, prefix=""):
    out = {}
    for k, v in d.items():
        if k.startswith("$") or not isinstance(v, dict):
            continue
        p = prefix + "." + k if prefix else k
        if "$value" in v:
            out[p] = v
        else:
            out.update(leaves(v, p))
    return out


def token_layers():
    layers = {}
    for layer, d in (("foundation", "00-foundation"), ("semantic", "10-semantic"), ("component", "20-component"), ("layout", "30-layout")):
        acc = {}
        for fn in sorted(os.listdir(rel("tokens", d))):
            if fn.endswith(".json"):
                acc.update(leaves(load("tokens", d, fn)))
        layers[layer] = acc
    return layers


def iter_cites(obj, where):
    if isinstance(obj, dict):
        if "cite" in obj and isinstance(obj["cite"], str):
            yield where, obj
        for k, v in obj.items():
            yield from iter_cites(v, where)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_cites(v, where)


def all_json():
    out = {}
    for f in repo_files():
        if f.endswith(".json"):
            out[f] = load(f)
    return out


def compute_counts():
    layers = token_layers()
    files = repo_files()
    templates = load("templates", "templates.json")
    cites = sum(1 for f, d in all_json().items() for _ in iter_cites(d, f))
    return {
        "sections": len([f for f in files if f.startswith("sections/")]),
        "primitives": len([f for f in files if f.startswith("primitives/")]),
        "components": len([f for f in files if f.startswith("components/")]),
        "templates": len(templates["templates"]),
        "routes": len(templates["routeInventory"]["routes"]),
        "foundationTokens": len(layers["foundation"]),
        "semanticTokens": len(layers["semantic"]),
        "componentTokens": len(layers["component"]),
        "layoutTokens": len(layers["layout"]),
        "themes": len([f for f in files if f.startswith("tokens/themes/")]),
        "graphRules": len(load("compatibility", "graph.json")["rules"]),
        "assetRoles": len(load("assets", "asset-roles.json")["roles"]),
        "citations": cites,
        "files": len(files),
    }


# ---------------------------------------------------------------- checks
def check_json():
    for f in repo_files():
        if f.endswith(".json"):
            try:
                load(f)
            except Exception as e:  # noqa: BLE001
                fail("json-parse", "%s: %s" % (f, e))


def check_schema_and_semantic():
    from jsonschema import Draft7Validator
    schema = load("schema", "pagespec.schema.json")
    try:
        Draft7Validator.check_schema(schema)
    except Exception as e:  # noqa: BLE001
        fail("schema", "pagespec.schema.json is not valid draft-07: %s" % e)
        return
    ex = load("schema", "example.pagespec.json")
    errs = list(Draft7Validator(schema).iter_errors(ex))
    for e in errs[:10]:
        fail("schema", "example: %s" % e.message[:200])
    import semantic_validate as sv
    errors, warnings = sv.validate(ex)
    for r, m in errors:
        fail("semantic", "example [%s] %s" % (r, m))
    for r, m in warnings:
        warn("semantic", "example [%s] %s" % (r, m))


def check_allowlist():
    al = load("tokens", "llm", "component-allowlist.json")
    schema = load("schema", "pagespec.schema.json")
    for kind, d in (("sections", "sections"), ("primitives", "primitives"), ("components", "components")):
        ids_files = {}
        for fn in sorted(os.listdir(rel(d))):
            if fn.endswith(".json"):
                c = load(d, fn)
                ids_files[c.get("id")] = fn
                expected = c["id"] + ".json" if kind == "sections" else c["id"].split(".", 1)[1] + ".json"
                if fn != expected:
                    fail("allowlist-parity", "%s/%s declares id %r (expected filename %s)" % (d, fn, c.get("id"), expected))
        listed = set(al[kind])
        for p in sorted(listed - set(ids_files)):
            fail("allowlist-parity", "phantom %s entry %r has no contract file" % (kind, p))
        for o in sorted(set(ids_files) - listed):
            fail("allowlist-parity", "orphan %s contract %r missing from allowlist" % (kind, o))
    # node / page / motion properties vs schema
    defs = schema["definitions"]
    for sid in al["sections"]:
        nd = defs.get("node.%s" % sid)
        if not nd:
            fail("allowlist-parity", "schema has no node.%s branch" % sid)
            continue
        if sorted(nd["properties"]) != sorted(al["nodeProperties"]):
            fail("allowlist-parity", "node.%s properties %s != allowlist.nodeProperties %s" % (sid, sorted(nd["properties"]), sorted(al["nodeProperties"])))
        md = defs["motion.%s" % sid]
        if sorted(md["properties"]) != sorted(al["motionProperties"]):
            fail("allowlist-parity", "motion.%s properties != allowlist.motionProperties" % sid)
        if md.get("additionalProperties") is not False:
            fail("motion-closed", "motion.%s is not additionalProperties:false" % sid)
    node_secs = sorted(k[5:] for k in defs if k.startswith("node."))
    if node_secs != sorted(al["sections"]):
        fail("allowlist-parity", "schema node branches %s != allowlist sections" % node_secs)
    if sorted(schema["properties"]) != sorted(al["pageProperties"]) or sorted(schema["required"]) != sorted(al["pageProperties"]):
        fail("allowlist-parity", "page properties/required != allowlist.pageProperties")
    if sorted(schema["properties"]["template"]["enum"]) != sorted(al["templates"]) or sorted(load("templates", "templates.json")["templates"]) != sorted(al["templates"]):
        fail("allowlist-parity", "templates enum / templates.json / allowlist.templates disagree")
    # asset roles
    reg = load("assets", "asset-roles.json")
    reg_ids = [r["id"] for r in reg["roles"]]
    if sorted(reg_ids) != sorted(al["assetRoles"]) or sorted(defs["assetRole"]["enum"]) != sorted(reg_ids):
        fail("asset-roles", "asset role ids differ across registry / allowlist / schema definitions.assetRole")
    used = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("assetRole", "iconRole", "tapMarkRole", "endpointRole") and isinstance(v, dict):
                    used.update(v.get("enum", [])) if "enum" in v else used.add(v.get("const"))
                elif k == "tapMarkRole" and isinstance(v, dict):
                    pass
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk({k: v for k, v in defs.items() if k != "assetRole"})
    walk(schema["properties"])
    if used != set(reg_ids):
        fail("asset-roles", "roles used by schema fields %s != registry %s" % (sorted(used), sorted(reg_ids)))
    if sorted(reg["generationPolicyEnum"]) != sorted(al["generationPolicies"]) or sorted(defs["generationPolicy"]["enum"]) != sorted(al["generationPolicies"]):
        fail("asset-roles", "generation policy vocabularies differ")
    for r in reg["roles"]:
        if r["generationPolicy"] not in reg["generationPolicyEnum"]:
            fail("asset-roles", "%s policy %r not in enum" % (r["id"], r["generationPolicy"]))
    # PINNED-VALUE check (MASTER-GUIDE 3.23): membership is not enough
    by_id = {r["id"]: r for r in reg["roles"]}
    for rid, pol in PINNED.items():
        if rid not in by_id:
            fail("asset-roles-pinned", "pinned role %s missing from registry" % rid)
        elif by_id[rid]["generationPolicy"] != pol:
            fail("asset-roles-pinned", "%s generationPolicy=%r, must be pinned to %r" % (rid, by_id[rid]["generationPolicy"], pol))
        if reg["pinned"].get(rid) != pol:
            fail("asset-roles-pinned", "registry.pinned[%s]=%r, must be %r" % (rid, reg["pinned"].get(rid), pol))
    if set(reg["pinned"]) != set(PINNED):
        fail("asset-roles-pinned", "registry.pinned keys %s != verify PINNED %s" % (sorted(reg["pinned"]), sorted(PINNED)))


def check_manifest():
    man = load("registry.manifest.json")
    al = load("tokens", "llm", "component-allowlist.json")
    if man.get("allowlistVersion") != al.get("version"):
        fail("allowlist-version", "manifest.allowlistVersion %r != component-allowlist.json version %r" % (man.get("allowlistVersion"), al.get("version")))
    if man.get("status") != "design-review-pending" or man.get("productionApproved") is not False:
        fail("manifest", "status must be design-review-pending and productionApproved false")
    for k in ("repositoryId", "versionFieldNote", "defaultTheme", "schemaValidatedThemes", "entryPoints", "counts"):
        if k not in man:
            fail("manifest", "missing %s" % k)
    real = compute_counts()
    for k, v in real.items():
        if man.get("counts", {}).get(k) != v:
            fail("manifest-counts", "counts.%s = %r, recomputed from disk = %r" % (k, man.get("counts", {}).get(k), v))
    for k in man.get("counts", {}):
        if k not in real:
            fail("manifest-counts", "counts.%s is not recomputable (unknown key)" % k)
    eps = man.get("entryPoints", {})
    for name, p in (eps.items() if isinstance(eps, dict) else enumerate(eps)):
        if p.startswith("/") or ".." in p.split("/") or re.match(r"^[A-Za-z]:", p):
            fail("entry-points", "%s=%r points outside design-repo/" % (name, p))
        elif not os.path.isfile(rel(p)):
            fail("entry-points", "%s=%r does not exist" % (name, p))
    if man.get("defaultTheme") not in man.get("schemaValidatedThemes", []):
        fail("manifest", "defaultTheme not in schemaValidatedThemes")
    for t in man.get("schemaValidatedThemes", []):
        if not os.path.isfile(rel("tokens", "themes", t + ".json")):
            fail("manifest", "theme %s has no tokens/themes file" % t)
    # README / CHANGELOG count parity
    for doc in ("README.md", "CHANGELOG.md"):
        with open(rel(doc), encoding="utf-8") as f:
            text = f.read()
        if doc == "README.md":
            for k, v in real.items():
                if not re.search(r"^\s*[-*]\s*%s:\s*%d\s*$" % (re.escape(k), v), text, re.M):
                    fail("readme-counts", "README.md does not state '- %s: %d'" % (k, v))
        if man.get("allowlistVersion") and man["allowlistVersion"] not in text:
            fail("doc-version", "%s does not mention allowlistVersion %s" % (doc, man["allowlistVersion"]))


def check_abs_paths():
    for f in repo_files():
        if f.endswith(".zip"):
            continue
        try:
            with open(rel(f), encoding="utf-8") as fh:
                text = fh.read()
        except UnicodeDecodeError:
            continue
        for pat in ABS_PATTERNS:
            for m in pat.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                fail("abs-path", "%s:%d contains an absolute local path" % (f, line))


def evidence_root(cli):
    root = cli or os.path.join(REPO, "..")
    root = os.path.abspath(root)
    present = os.path.isfile(os.path.join(root, "CLONE_SPEC.md"))
    return root, present


_CITE = re.compile(r"^(.+):(\d+)(?:-(\d+))?$")


def check_citations(root, present):
    n = 0
    cache = {}
    for f, d in all_json().items():
        for where, c in iter_cites(d, f):
            n += 1
            m = _CITE.match(c["cite"])
            if not m:
                fail("citations", "%s: malformed cite %r" % (f, c["cite"]))
                continue
            path, a, b = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
            if path.startswith("/") or ".." in path.split("/"):
                fail("citations", "%s: cite path %r must be relative to the evidence root" % (f, path))
                continue
            if not c.get("quote"):
                fail("citations", "%s: cite %r has no quote" % (f, c["cite"]))
            if not present:
                continue
            full = os.path.join(root, path)
            if path not in cache:
                if not os.path.isfile(full):
                    cache[path] = None
                else:
                    with open(full, encoding="utf-8", errors="replace") as fh:
                        cache[path] = fh.read().split("\n")
            L = cache[path]
            if L is None:
                fail("citations", "%s: cited file %r does not exist under evidence root" % (f, path))
                continue
            if a < 1 or b < a or b > len(L):
                fail("citations", "%s: %s out of range (file has %d lines)" % (f, c["cite"], len(L)))
                continue
            if c.get("quote") and c["quote"] not in "\n".join(L[a - 1:b]):
                fail("citations", "%s: %s does not contain quote %r (in range but wrong content)" % (f, c["cite"], c["quote"][:60]))
    if not present:
        warn("citations", "evidence root %s has no CLONE_SPEC.md (standalone copy): %d citations NOT resolved, format-checked only" % (os.path.basename(root) or root, n))
    return n


def check_graph_validator():
    import semantic_validate as sv
    g = load("compatibility", "graph.json")
    ids = [r["id"] for r in g["rules"]]
    if len(ids) != len(set(ids)):
        fail("graph", "duplicate rule ids")
    if set(ids) != sv.RULES:
        fail("graph-validator-parity", "graph-only %s / validator-only %s" % (sorted(set(ids) - sv.RULES), sorted(sv.RULES - set(ids))))
    with open(rel("schema", "semantic_validate.py"), encoding="utf-8") as f:
        src = f.read()
    secs = set(load("tokens", "llm", "component-allowlist.json")["sections"])
    for r in g["rules"]:
        if r["severity"] not in ("error", "warn"):
            fail("graph", "%s severity %r" % (r["id"], r["severity"]))
        fn = r["enforcedBy"].split(".")[-1]
        if "def %s(" % fn not in src:
            fail("graph-validator-parity", "%s enforcedBy %s, no such function in semantic_validate.py" % (r["id"], r["enforcedBy"]))
        for e in r.get("exceptions", []):
            for s in e.get("pair", []) + ([e["section"]] if "section" in e else []):
                if s not in secs:
                    fail("graph", "%s exception references unknown section %r" % (r["id"], s))


def check_templates():
    t = load("templates", "templates.json")
    secs = set(load("tokens", "llm", "component-allowlist.json")["sections"])
    routes = [r["path"] for r in t["routeInventory"]["routes"]]
    if len(routes) != len(set(routes)):
        fail("routes", "duplicate route in inventory")
    mapped = {}
    for tid, tpl in t["templates"].items():
        if tpl.get("id") != tid:
            fail("templates", "%s id mismatch" % tid)
        for r in tpl["routes"]:
            mapped.setdefault(r, []).append(tid)
        for n in tpl["nodes"]:
            if not isinstance(n, dict) or not isinstance(n.get("required"), bool) or not isinstance(n.get("repeatable"), bool):
                fail("templates", "%s node %r must be an object with boolean required/repeatable" % (tid, n))
            elif n["section"] not in secs:
                fail("templates", "%s node section %r not in allowlist" % (tid, n["section"]))
    for r in routes:
        if len(mapped.get(r, [])) != 1:
            fail("routes", "route %s mapped to %s (must be exactly one template)" % (r, mapped.get(r)))
    for r in mapped:
        if r not in routes:
            fail("routes", "template route %s missing from routeInventory" % r)
    schema = load("schema", "pagespec.schema.json")
    if sorted(schema["properties"]["route"]["enum"]) != sorted(routes):
        fail("routes", "schema route enum != routeInventory")


def check_ia(root, present):
    p = os.path.join(root, "ia.json")
    if not present or not os.path.isfile(p):
        warn("ia-parity", "no sibling ia.json; skipped")
        return
    with open(p, encoding="utf-8") as f:
        ia = json.load(f)
    t = load("templates", "templates.json")["templates"]
    for it in ia.get("templates", []):
        mine = t.get(it["id"])
        if not mine:
            fail("ia-parity", "ia.json template %s not in templates.json" % it["id"])
            continue
        if [n["section"] for n in mine["nodes"]] != it["sections"]:
            fail("ia-parity", "%s node order differs from ia.json" % it["id"])
        if sorted(mine["routes"]) != sorted(it["routes"]):
            fail("ia-parity", "%s routes differ from ia.json" % it["id"])
    secs = load("tokens", "llm", "component-allowlist.json")["sections"]
    if sorted(secs) != sorted(ia.get("sections", {})):
        fail("ia-parity", "section ids differ from ia.json")
    for sid, s in ia.get("sections", {}).items():
        if sid in secs:
            c = load("sections", sid + ".json")
            if c["category"] != s["category"].lower():
                fail("ia-parity", "%s category %r != ia.json %r" % (sid, c["category"], s["category"]))
            if not s.get("implementedBy", "").startswith(c["implementedBy"]):
                fail("ia-parity", "%s implementedBy %r vs ia.json %r" % (sid, c["implementedBy"], s.get("implementedBy")))


def check_tokens():
    layers = token_layers()
    allt = {}
    for d in layers.values():
        allt.update(d)
    cat = load("tokens", "llm", "token-catalog.json")
    cpaths = {e["path"]: (k, e) for k, es in cat["categories"].items() for e in es}
    for p in allt:
        if p not in cpaths:
            fail("token-catalog", "token %s missing from catalog" % p)
    for p in cpaths:
        if p not in allt:
            fail("token-catalog", "catalog path %s resolves to no token" % p)

    def resolve(p, depth=0):
        v = allt[p]["$value"]
        if isinstance(v, str) and v.startswith("{") and v.endswith("}"):
            if depth > 8 or v[1:-1] not in allt:
                return None
            return resolve(v[1:-1], depth + 1)
        return v
    for p, v in allt.items():
        val = v["$value"]
        if isinstance(val, str) and val.startswith("{"):
            if val[1:-1] not in allt:
                fail("token-alias", "%s -> %s unresolved" % (p, val))
            elif p.startswith("semantic.") and not val[1:-1].split(".")[0] in ("color", "typography"):
                fail("token-alias", "semantic %s must alias a foundation token, got %s" % (p, val))
    theme = load("tokens", "themes", "light.json")
    sem = {p for p in allt if p.startswith("semantic.")}
    if set(theme["resolves"]) != sem:
        fail("theme", "light.json resolves %d tokens, semantic layer has %d" % (len(theme["resolves"]), len(sem)))
    for p, r in theme["resolves"].items():
        if p in allt and r["value"] != resolve(p):
            fail("theme", "light.json %s=%r but resolves to %r" % (p, r["value"], resolve(p)))
    pol = load("tokens", "llm", "token-policy.json")
    for k in pol["rawValueRestrictions"]:
        if k not in cat["categories"]:
            fail("token-policy", "rawValueRestrictions key %r is not a real catalog category %s" % (k, sorted(cat["categories"])))
    schema = load("schema", "pagespec.schema.json")
    for dn in ("thumbColorToken", "sourceDotColorToken"):
        for p in schema["definitions"][dn]["enum"]:
            if p not in cpaths:
                fail("token-catalog", "schema %s value %s not in catalog" % (dn, p))
            elif cpaths[p][1].get("restricted"):
                fail("token-catalog", "schema %s allows restricted token %s" % (dn, p))
    for d in ("primitives", "components"):
        for fn in os.listdir(rel(d)):
            if fn.endswith(".json"):
                for p in load(d, fn).get("tokens", []):
                    if p not in cpaths:
                        fail("token-refs", "%s/%s references unknown token %s" % (d, fn, p))
    for fn in os.listdir(rel("sections")):
        if fn.endswith(".json"):
            s = load("sections", fn)
            if not s.get("responsive"):
                fail("responsive", "%s has no structured responsive field" % s["id"])
            for r in s.get("responsive", []):
                if r["breakpoint"] not in cpaths:
                    fail("responsive", "%s responsive breakpoint %s not a token" % (s["id"], r["breakpoint"]))
                if not r.get("evidence"):
                    fail("responsive", "%s responsive entry %r has no CSS evidence" % (s["id"], r["target"]))


def _strings_without_budget(node, path, out, defs):
    if isinstance(node, dict):
        if node.get("type") == "string" and "x-maxWords" not in node:
            out.append(path)
        for k, v in node.items():
            _strings_without_budget(v, path + "/" + k, out, defs)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _strings_without_budget(v, "%s/%d" % (path, i), out, defs)


def check_section_schema_parity():
    schema = load("schema", "pagespec.schema.json")
    defs = schema["definitions"]
    for fn in sorted(os.listdir(rel("sections"))):
        if not fn.endswith(".json"):
            continue
        s = load("sections", fn)
        sid = s["id"]
        if defs.get("content.%s" % sid) != s["contentSchema"]:
            fail("schema-contract-parity", "%s contentSchema differs from schema definitions.content.%s" % (sid, sid))
        if defs.get("motion.%s" % sid) != s["motionSchema"]:
            fail("schema-contract-parity", "%s motionSchema differs from schema definitions.motion.%s" % (sid, sid))
        ms = s["motionSchema"]["properties"]
        if ms["reducedMotionFallback"].get("const") != s["motion"]["reducedMotionFallback"] or ms["pattern"]["enum"] != [s["motion"]["pattern"]] or ms["secondary"].get("const") != s["motion"]["secondary"]:
            fail("schema-contract-parity", "%s motion block disagrees with its own motionSchema" % sid)
        if s["contentSchema"].get("additionalProperties") is not False:
            fail("closed-content", "%s contentSchema not additionalProperties:false" % sid)
    missing = []
    _strings_without_budget(defs, "#/definitions", missing, defs)
    _strings_without_budget(schema["properties"], "#/properties", missing, defs)
    for m in missing:
        fail("max-words", "free-text string without x-maxWords: %s" % m)

    def closed(node, path):
        if isinstance(node, dict):
            if node.get("type") == "object" and node.get("additionalProperties") is not False:
                fail("closed-objects", "object without additionalProperties:false at %s" % path)
            for k, v in node.items():
                closed(v, path + "/" + k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                closed(v, "%s/%d" % (path, i))
    closed(schema, "#")


def check_referenced_scripts():
    for p in ("extraction/prove_drift.py", "schema/semantic_validate.py", "schema/tests/adversarial_test.py"):
        if not os.path.isfile(rel(p)):
            fail("referenced-scripts", "%s is referenced by docs but missing" % p)


def main(argv):
    cli_root = None
    if "--evidence-root" in argv:
        cli_root = argv[argv.index("--evidence-root") + 1]
    root, present = evidence_root(cli_root)
    steps = [
        ("json-parse", check_json),
        ("schema+semantic", check_schema_and_semantic),
        ("allowlist/asset-roles/pinned", check_allowlist),
        ("manifest/counts/entryPoints/docs", check_manifest),
        ("abs-paths", check_abs_paths),
        ("citations", lambda: check_citations(root, present)),
        ("graph<->validator", check_graph_validator),
        ("templates/routes", check_templates),
        ("ia.json parity", lambda: check_ia(root, present)),
        ("tokens/catalog/policy/theme", check_tokens),
        ("schema<->contract/maxWords/closed", check_section_schema_parity),
        ("referenced scripts", check_referenced_scripts),
    ]
    for name, fn in steps:
        before = len(FAILS)
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            fail(name, "check crashed: %r" % (e,))
        print("%-38s %s" % (name, "ok" if len(FAILS) == before else "FAIL (%d)" % (len(FAILS) - before)))
    print("evidence root: %s" % ("present (sibling project)" if present else "ABSENT (standalone) -> citation checks WARN"))
    for c, m in WARNS:
        print("WARN [%s] %s" % (c, m))
    for c, m in FAILS:
        print("FAIL [%s] %s" % (c, m))
    print("verify_all: %s (%d fail, %d warn)" % ("PASS" if not FAILS else "FAIL", len(FAILS), len(WARNS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
