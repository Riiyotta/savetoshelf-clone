#!/usr/bin/env python3
"""Semantic validator for Shelf homepage PageSpecs.

Usage:  python3 schema/semantic_validate.py [path/to/pagespec.json]
        (defaults to schema/example.pagespec.json)
Exit 0 = no errors (warnings allowed), 1 = errors.

Enforces what JSON Schema cannot: the declared template's real node list,
route binding, rhythm/position rules from compatibility/graph.json (respecting
severity), anchor resolution, const-locked signature motion cross-checked
against the section contracts, per-instance x-maxWords, the pinned endpoint
policy, and real-brand guards for generated pages.

Every rule id in RULES must equal the rule ids in compatibility/graph.json
(extraction/verify_all.py fails otherwise).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

RULES = {
    "SCHEMA_VALID", "TEMPLATE_DECLARED_AND_ROUTE_BOUND", "TEMPLATE_SEQUENCE_MATCH", "ONE_PER_PAGE",
    "NAV_FIRST", "FOOTER_LAST", "ONE_HERO", "BOOKMARK_HEADER_SEQUENCE", "FINDING_FOLLOWS_BOOKMARK",
    "WAITLIST_PRECEDES_FOOTER", "NAV_ANCHORS_RESOLVE", "NAV_CTA_TARGETS_HERO_WAITLIST",
    "NO_ADJACENT_SAME_CATEGORY", "REDUCED_MOTION_FALLBACK_REQUIRED", "SIGNATURE_MOTION_LOCKED",
    "MAX_WORDS", "COLOR_TOKEN_IN_CATALOG", "ENDPOINT_POLICY_PINNED", "GENERATED_NO_REAL_BRAND_ASSETS",
    "GENERATED_NO_REAL_BRAND_TEXT",
}
NO_HERO_TEMPLATES = set()  # no hero-less template exists; mirrors graph ONE_HERO.exceptionNote
PRIMARY_HERO = "hero.intro"
HERO_COMPANION = "hero.demo-mockup"
BOOKMARK_SEQ = ["hero.intro", "hero.demo-mockup", "story.why-funnel"]
REAL_BRAND_TEXT = ["shelf", "savetoshelf"]


def load(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return json.load(f)


class Ctx:
    def __init__(self):
        self.schema = load("schema/pagespec.schema.json")
        self.templates = load("templates/templates.json")["templates"]
        self.graph = load("compatibility/graph.json")
        self.severity = {r["id"]: r["severity"] for r in self.graph["rules"]}
        self.rules = {r["id"]: r for r in self.graph["rules"]}
        self.roles = load("assets/asset-roles.json")
        self.catalog = load("tokens/llm/token-catalog.json")
        self.sections = {}
        sdir = os.path.join(REPO, "sections")
        for fn in sorted(os.listdir(sdir)):
            if fn.endswith(".json"):
                with open(os.path.join(sdir, fn), encoding="utf-8") as f:
                    s = json.load(f)
                self.sections[s["id"]] = s


_CTX = None


def ctx():
    global _CTX
    if _CTX is None:
        _CTX = Ctx()
    return _CTX


class Report:
    def __init__(self, c):
        self.c = c
        self.errors, self.warnings = [], []

    def add(self, rule, msg):
        assert rule in RULES, rule
        sev = self.c.severity.get(rule, "error")
        (self.errors if sev == "error" else self.warnings).append((rule, msg))


def secs(spec):
    return [n.get("section") for n in spec.get("nodes", []) if isinstance(n, dict)]


# ---------------------------------------------------------------- checks
def check_schema(spec, r):
    try:
        from jsonschema import Draft7Validator
    except ImportError:  # pragma: no cover
        r.add("SCHEMA_VALID", "jsonschema not installed; pip install jsonschema")
        return False
    errs = sorted(Draft7Validator(r.c.schema).iter_errors(spec), key=lambda e: list(e.path))
    for e in errs[:25]:
        r.add("SCHEMA_VALID", "%s: %s" % ("/".join(map(str, e.path)) or "<root>", e.message[:240]))
    return not errs


def check_template_binding(spec, r):
    t = r.c.templates.get(spec.get("template"))
    if not t:
        r.add("TEMPLATE_DECLARED_AND_ROUTE_BOUND", "unknown template %r" % spec.get("template"))
        return None
    if spec.get("route") not in t["routes"]:
        r.add("TEMPLATE_DECLARED_AND_ROUTE_BOUND", "route %r not bound to template %s (routes %s)" % (spec.get("route"), t["id"], t["routes"]))
    return t


def check_template_sequence(spec, r, t):
    if t is None:
        return
    tnodes = t["nodes"]
    allowed = [n["section"] for n in tnodes]
    got = secs(spec)
    for s in got:
        if s not in allowed:
            r.add("TEMPLATE_SEQUENCE_MATCH", "section %r is not part of template %s" % (s, t["id"]))
    for n in tnodes:
        cnt = got.count(n["section"])
        if n["required"] and cnt == 0:
            r.add("TEMPLATE_SEQUENCE_MATCH", "required node %r of template %s is missing" % (n["section"], t["id"]))
        if not n["repeatable"] and cnt > 1:
            r.add("TEMPLATE_SEQUENCE_MATCH", "non-repeatable node %r appears %d times" % (n["section"], cnt))
    # order: the template-known sections, de-duplicated, must follow template order
    seen = []
    for s in got:
        if s in allowed and s not in seen:
            seen.append(s)
    idx = [allowed.index(s) for s in seen]
    if idx != sorted(idx):
        r.add("TEMPLATE_SEQUENCE_MATCH", "node order %s does not follow template %s order %s" % (seen, t["id"], allowed))


def check_one_per_page(spec, r):
    keys = {}
    for n in spec.get("nodes", []):
        if not isinstance(n, dict):
            continue
        k = (n.get("section"), n.get("variant"))
        keys[k] = keys.get(k, 0) + 1
    for (s, v), cnt in keys.items():
        con = r.c.sections.get(s, {}).get("constraints", {})
        if con.get("onePerPage") and cnt > 1:
            r.add("ONE_PER_PAGE", "(%s, %s) appears %d times" % (s, v, cnt))


def check_positions(spec, r):
    got = secs(spec)
    if not got:
        return
    if got[0] != "chrome.floating-nav":
        r.add("NAV_FIRST", "first node is %r, expected chrome.floating-nav" % got[0])
    if got[-1] != "chrome.footer":
        r.add("FOOTER_LAST", "last node is %r, expected chrome.footer" % got[-1])

    def follows(a, b, rule):
        if b in got:
            i = got.index(b)
            if a not in got or i == 0 or got[i - 1] != a:
                r.add(rule, "%s must immediately follow %s" % (b, a))
    follows("story.why-funnel", "story.finding", "FINDING_FOLLOWS_BOOKMARK")
    if "conversion.closing-waitlist" in got:
        i = got.index("conversion.closing-waitlist")
        if i + 1 >= len(got) or got[i + 1] != "chrome.footer":
            r.add("WAITLIST_PRECEDES_FOOTER", "conversion.closing-waitlist must immediately precede chrome.footer")


def check_one_hero(spec, r):
    if spec.get("template") in NO_HERO_TEMPLATES:
        return
    got = secs(spec)
    n = got.count(PRIMARY_HERO)
    if n != 1:
        r.add("ONE_HERO", "expected exactly one %s, found %d" % (PRIMARY_HERO, n))
    for i, s in enumerate(got):
        if s and s.startswith("hero.") and s not in (PRIMARY_HERO, HERO_COMPANION):
            r.add("ONE_HERO", "unexpected hero section %r" % s)
        if s == HERO_COMPANION and (i == 0 or got[i - 1] != PRIMARY_HERO):
            r.add("ONE_HERO", "%s is only allowed directly after %s" % (HERO_COMPANION, PRIMARY_HERO))


def check_bookmark_header(spec, r):
    got = secs(spec)
    if "chrome.floating-nav" not in got:
        r.add("BOOKMARK_HEADER_SEQUENCE", "cannot place bookmark header: chrome.floating-nav missing")
        return
    i = got.index("chrome.floating-nav")
    if got[i + 1:i + 1 + len(BOOKMARK_SEQ)] != BOOKMARK_SEQ:
        r.add("BOOKMARK_HEADER_SEQUENCE", "nodes after nav must be %s, got %s" % (BOOKMARK_SEQ, got[i + 1:i + 1 + len(BOOKMARK_SEQ)]))


def check_anchors(spec, r):
    present = {}
    for n in spec.get("nodes", []):
        if isinstance(n, dict) and n.get("section") in r.c.sections:
            a = r.c.sections[n["section"]].get("anchorId")
            if a:
                present[a] = n["section"]
    for n in spec.get("nodes", []):
        if not isinstance(n, dict) or n.get("section") != "chrome.floating-nav":
            continue
        content = n.get("content", {}) or {}
        for link in content.get("links", []) or []:
            anc = str(link.get("anchor", "")).lstrip("#")
            if anc not in present:
                r.add("NAV_ANCHORS_RESOLVE", "nav link %r targets #%s which no section on this page provides" % (link.get("label"), anc))
        cta = content.get("cta", {}) or {}
        if cta.get("href") == "#waitlist" and present.get("waitlist") != PRIMARY_HERO:
            r.add("NAV_CTA_TARGETS_HERO_WAITLIST", "nav CTA #waitlist needs %s on the page" % PRIMARY_HERO)


def check_rhythm(spec, r):
    rule = r.c.rules["NO_ADJACENT_SAME_CATEGORY"]
    exc = {tuple(e["pair"]) for e in rule["exceptions"]}
    got = secs(spec)
    for a, b in zip(got, got[1:]):
        ca = r.c.sections.get(a, {}).get("category")
        cb = r.c.sections.get(b, {}).get("category")
        if ca and ca == cb and (a, b) not in exc:
            r.add("NO_ADJACENT_SAME_CATEGORY", "%s -> %s share category %r with no named exception" % (a, b, ca))


def check_motion(spec, r):
    for i, n in enumerate(spec.get("nodes", [])):
        if not isinstance(n, dict):
            continue
        m = n.get("motion")
        if not isinstance(m, dict) or not m.get("reducedMotionFallback"):
            r.add("REDUCED_MOTION_FALLBACK_REQUIRED", "nodes[%d] (%s) has no motion.reducedMotionFallback" % (i, n.get("section")))
            continue
        con = r.c.sections.get(n.get("section"), {}).get("motion")
        if not con:
            continue
        for k in ("pattern", "secondary", "reducedMotionFallback"):
            if m.get(k) != con[k]:
                r.add("SIGNATURE_MOTION_LOCKED", "nodes[%d] (%s) motion.%s=%r, contract requires %r" % (i, n["section"], k, m.get(k), con[k]))


def _resolve(schema, node):
    while isinstance(node, dict) and "$ref" in node:
        path = node["$ref"].lstrip("#/").split("/")
        node = schema
        for p in path:
            node = node[p]
    return node


def _walk_words(schema, snode, inst, path, r):
    snode = _resolve(schema, snode)
    if not isinstance(snode, dict):
        return
    if isinstance(inst, str) and "x-maxWords" in snode:
        n = len(inst.split())
        if n > snode["x-maxWords"]:
            r.add("MAX_WORDS", "%s has %d words, max %d" % (path, n, snode["x-maxWords"]))
    elif isinstance(inst, dict):
        props = snode.get("properties", {})
        for k, v in inst.items():
            if k in props:
                _walk_words(schema, props[k], v, "%s.%s" % (path, k), r)
    elif isinstance(inst, list):
        items = snode.get("items")
        for i, v in enumerate(inst):
            sub = items[i] if isinstance(items, list) and i < len(items) else (items if isinstance(items, dict) else None)
            if sub is not None:
                _walk_words(schema, sub, v, "%s[%d]" % (path, i), r)


def check_max_words(spec, r):
    sch = r.c.schema
    _walk_words(sch, sch["properties"]["meta"], spec.get("meta"), "meta", r)
    for i, n in enumerate(spec.get("nodes", [])):
        if isinstance(n, dict) and ("content.%s" % n.get("section")) in sch["definitions"]:
            _walk_words(sch, sch["definitions"]["content.%s" % n["section"]], n.get("content"), "nodes[%d](%s).content" % (i, n["section"]), r)


def _iter(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield path + "." + k, k, v
            yield from _iter(v, path + "." + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _iter(v, "%s[%d]" % (path, i))


def check_color_tokens(spec, r):
    cat = {}
    for entries in r.c.catalog["categories"].values():
        for e in entries:
            cat[e["path"]] = e
    for p, k, v in _iter(spec.get("nodes", []), "nodes"):
        if k == "colorToken":
            if v not in cat:
                r.add("COLOR_TOKEN_IN_CATALOG", "%s=%r not in token catalog" % (p, v))
            elif cat[v].get("restricted"):
                r.add("COLOR_TOKEN_IN_CATALOG", "%s=%r is restricted (%s)" % (p, v, cat[v]["restricted"]))


def check_endpoint_policy(spec, r):
    pinned = r.c.roles["pinned"]
    for p, k, v in _iter(spec.get("nodes", []), "nodes"):
        if k == "form" and isinstance(v, dict):
            role = v.get("endpointRole")
            want = pinned.get(role)
            if want is None:
                r.add("ENDPOINT_POLICY_PINNED", "%s.endpointRole %r has no pinned policy" % (p, role))
            elif v.get("endpointPolicy") != want:
                r.add("ENDPOINT_POLICY_PINNED", "%s.endpointPolicy=%r but %s is pinned to %r" % (p, v.get("endpointPolicy"), role, want))


ROLE_KEYS = ("assetRole", "iconRole", "tapMarkRole", "endpointRole")


def check_generated_brand(spec, r):
    if spec.get("purpose") != "generated":
        return
    banned = {rid for rid, pol in r.c.roles["pinned"].items() if pol == "must-not-reproduce-real-brand"}
    for p, k, v in _iter({"meta": spec.get("meta"), "nodes": spec.get("nodes", [])}):
        if k in ROLE_KEYS and v in banned:
            r.add("GENERATED_NO_REAL_BRAND_ASSETS", "%s=%r is a real-brand role (must-not-reproduce-real-brand)" % (p, v))
        if isinstance(v, str) and k not in ROLE_KEYS:
            low = v.lower()
            for w in REAL_BRAND_TEXT:
                if w in low:
                    r.add("GENERATED_NO_REAL_BRAND_TEXT", "%s contains real brand text %r" % (p, w))
                    break


def validate(spec):
    """Return (errors, warnings): lists of (rule_id, message)."""
    c = ctx()
    r = Report(c)
    if not isinstance(spec, dict):
        r.add("SCHEMA_VALID", "PageSpec must be an object")
        return r.errors, r.warnings
    check_schema(spec, r)
    t = check_template_binding(spec, r)
    check_template_sequence(spec, r, t)
    check_one_per_page(spec, r)
    check_positions(spec, r)
    check_one_hero(spec, r)
    check_bookmark_header(spec, r)
    check_anchors(spec, r)
    check_rhythm(spec, r)
    check_motion(spec, r)
    check_max_words(spec, r)
    check_color_tokens(spec, r)
    check_endpoint_policy(spec, r)
    check_generated_brand(spec, r)
    return r.errors, r.warnings


def main(argv):
    path = argv[1] if len(argv) > 1 else os.path.join(HERE, "example.pagespec.json")
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    errors, warnings = validate(spec)
    for rule, msg in warnings:
        print("WARN  [%s] %s" % (rule, msg))
    for rule, msg in errors:
        print("ERROR [%s] %s" % (rule, msg))
    print("semantic_validate: %s -> %d error(s), %d warning(s)" % (os.path.basename(path), len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
