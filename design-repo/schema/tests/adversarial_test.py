#!/usr/bin/env python3
"""Adversarial suite: every mutation must be REJECTED (by the expected rule),
every control must PASS with zero errors.

Usage: python3 schema/tests/adversarial_test.py   (exit 0 = all good)
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(SCHEMA_DIR)
sys.path.insert(0, SCHEMA_DIR)
import semantic_validate as sv  # noqa: E402
from jsonschema import Draft7Validator  # noqa: E402

with open(os.path.join(SCHEMA_DIR, "example.pagespec.json"), encoding="utf-8") as f:
    EXAMPLE = json.load(f)
with open(os.path.join(SCHEMA_DIR, "pagespec.schema.json"), encoding="utf-8") as f:
    SCHEMA = json.load(f)
with open(os.path.join(REPO, "templates", "templates.json"), encoding="utf-8") as f:
    TEMPLATES = json.load(f)["templates"]
SCHEMA_V = Draft7Validator(SCHEMA)


def node(spec, sid):
    for n in spec["nodes"]:
        if n["section"] == sid:
            return n
    raise KeyError(sid)


def idx(spec, sid):
    return [n["section"] for n in spec["nodes"]].index(sid)


def long_text(n):
    return " ".join(["word"] * n)


# (name, layer, mutate(spec), expected_rule)
MUTATIONS = [
    # ---- schema layer (Draft-07 alone must reject)
    ("S01 unknown template", "schema", lambda s: s.update(template="template.blog"), "SCHEMA_VALID"),
    ("S02 node without motion", "schema", lambda s: node(s, "support.faq").pop("motion"), "SCHEMA_VALID"),
    ("S03 motion without reducedMotionFallback", "schema", lambda s: node(s, "story.finding")["motion"].pop("reducedMotionFallback"), "SCHEMA_VALID"),
    ("S04 funnel fallback swapped to another valid fallback", "schema", lambda s: node(s, "story.why-funnel")["motion"].update(reducedMotionFallback="static-no-motion"), "SCHEMA_VALID"),
    ("S05 funnel signature motion degraded to fade", "schema", lambda s: node(s, "story.why-funnel")["motion"].update(pattern="fade-up"), "SCHEMA_VALID"),
    ("S06 invented motion field", "schema", lambda s: node(s, "hero.intro")["motion"].update(inventedAnimation="spin"), "SCHEMA_VALID"),
    ("S07 invented section type", "schema", lambda s: s["nodes"].insert(2, {"section": "hero.split", "variant": "default", "content": {}, "motion": {}}), "SCHEMA_VALID"),
    ("S08 invented asset role", "schema", lambda s: node(s, "chrome.floating-nav")["content"]["logo"].update(assetRole="photo.founder"), "SCHEMA_VALID"),
    ("S09 live endpoint as submit target", "schema", lambda s: node(s, "hero.intro")["content"]["form"].update(submitTarget="/api/waitlist"), "SCHEMA_VALID"),
    ("S10 extra content property", "schema", lambda s: node(s, "chrome.footer")["content"].update(socialLinks=["x"]), "SCHEMA_VALID"),
    ("S11 nav anchor to a non-existent route", "schema", lambda s: node(s, "chrome.floating-nav")["content"]["links"][0].update(anchor="#pricing"), "SCHEMA_VALID"),
    ("S12 saving step visuals reordered", "schema", lambda s: node(s, "story.saving-steps")["content"]["steps"].reverse(), "SCHEMA_VALID"),
    ("S13 missing required hero subhead", "schema", lambda s: node(s, "hero.intro")["content"].pop("subhead"), "SCHEMA_VALID"),
    ("S14 seventh FAQ item", "schema", lambda s: node(s, "support.faq")["content"]["items"].append({"question": "Q?", "answer": "A."}), "SCHEMA_VALID"),
    ("S15 wrong pageSpecVersion", "schema", lambda s: s.update(pageSpecVersion="2.0.0"), "SCHEMA_VALID"),
    ("S16 raw hex instead of colorToken", "schema", lambda s: node(s, "hero.demo-mockup")["content"]["cards"][0]["thumb"].update(colorToken="#ff0000"), "SCHEMA_VALID"),
    ("S17 restricted third-party brand colour as thumb", "schema", lambda s: node(s, "story.finding")["content"]["palette"]["hits"][0]["thumb"].update(colorToken="color.third-party-brand.youtube"), "SCHEMA_VALID"),
    ("S18 thumbnail as photo role", "schema", lambda s: node(s, "hero.demo-mockup")["content"]["cards"][1]["thumb"].update(assetRole="brand.logo-mark"), "SCHEMA_VALID"),
    ("S19 unknown route", "schema", lambda s: s.update(route="/pricing"), "SCHEMA_VALID"),
    ("S20 extra page-level property", "schema", lambda s: s.update(analytics="plausible"), "SCHEMA_VALID"),
    # ---- structural layer (schema passes, semantic rules reject)
    ("T01 duplicate one-per-page FAQ", "structural", lambda s: s["nodes"].insert(idx(s, "support.faq"), copy.deepcopy(node(s, "support.faq"))), "ONE_PER_PAGE"),
    ("T02 mandatory footer removed", "structural", lambda s: s["nodes"].pop(idx(s, "chrome.footer")), "TEMPLATE_SEQUENCE_MATCH"),
    ("T03 finding and saving swapped", "structural", lambda s: s["nodes"].insert(idx(s, "story.finding"), s["nodes"].pop(idx(s, "story.saving-steps"))), "TEMPLATE_SEQUENCE_MATCH"),
    ("T04 nav not first", "structural", lambda s: s["nodes"].insert(1, s["nodes"].pop(0)), "NAV_FIRST"),
    ("T05 demo mockup removed (template/node mismatch)", "structural", lambda s: s["nodes"].pop(idx(s, "hero.demo-mockup")), "TEMPLATE_SEQUENCE_MATCH"),
    ("T06 funnel moved before demo (bookmark header broken)", "structural", lambda s: s["nodes"].insert(idx(s, "hero.demo-mockup"), s["nodes"].pop(idx(s, "story.why-funnel"))), "BOOKMARK_HEADER_SEQUENCE"),
    ("T07 FAQ removed -> nav anchor dangles", "structural", lambda s: s["nodes"].pop(idx(s, "support.faq")), "NAV_ANCHORS_RESOLVE"),
    ("T08 hero removed -> nav CTA dangles", "structural", lambda s: s["nodes"].pop(idx(s, "hero.intro")), "NAV_CTA_TARGETS_HERO_WAITLIST"),
    ("T09 closing waitlist moved off the footer", "structural", lambda s: s["nodes"].insert(idx(s, "support.faq"), s["nodes"].pop(idx(s, "conversion.closing-waitlist"))), "WAITLIST_PRECEDES_FOOTER"),
    ("T10 finding detached from funnel", "structural", lambda s: s["nodes"].insert(idx(s, "story.finding"), s["nodes"].pop(idx(s, "support.faq"))), "FINDING_FOLLOWS_BOOKMARK"),
    ("T11 second primary hero", "structural", lambda s: s["nodes"].insert(idx(s, "hero.intro") + 1, copy.deepcopy(node(s, "hero.intro"))), "ONE_HERO"),
    ("T12 endpointPolicy -> may-generate-new (valid enum, wrong pinned value)", "structural", lambda s: node(s, "hero.intro")["content"]["form"].update(endpointPolicy="may-generate-new"), "ENDPOINT_POLICY_PINNED"),
    ("T13 closing endpointPolicy -> css-color-block-only (valid enum, wrong pinned value)", "structural", lambda s: node(s, "conversion.closing-waitlist")["content"]["form"].update(endpointPolicy="css-color-block-only"), "ENDPOINT_POLICY_PINNED"),
    ("T14 generated page reuses the real Shelf logo", "structural", lambda s: s.update(purpose="generated"), "GENERATED_NO_REAL_BRAND_ASSETS"),
    ("T15 generated page keeps third-party brand tag icons", "structural", lambda s: _generated_clean(s) or node(s, "story.why-funnel")["content"]["tags"][0].update(iconRole="icon.third-party-brand"), "GENERATED_NO_REAL_BRAND_ASSETS"),
    ("B01 template declared vs route mismatch (schema enum AND semantic backstop both fire)", "both", lambda s: _route_mismatch(s), "TEMPLATE_DECLARED_AND_ROUTE_BOUND"),
    # ---- runtime word budgets (schema passes, MAX_WORDS rejects)
    ("R01 hero headline over budget", "runtime", lambda s: node(s, "hero.intro")["content"].update(headlineLine1=long_text(9)), "MAX_WORDS"),
    ("R02 FAQ answer over budget (nested array)", "runtime", lambda s: node(s, "support.faq")["content"]["items"][3].update(answer=long_text(60)), "MAX_WORDS"),
    ("R03 palette question over budget ($ref'd def)", "runtime", lambda s: node(s, "hero.demo-mockup")["content"]["palette"].update(question=long_text(30)), "MAX_WORDS"),
    ("R04 meta title over budget", "runtime", lambda s: s["meta"].update(title=long_text(20)), "MAX_WORDS"),
    ("R05 waitlist form done copy over budget", "runtime", lambda s: node(s, "conversion.closing-waitlist")["content"]["form"].update(doneBody=long_text(25)), "MAX_WORDS"),
    ("R06 saving step body over budget (tuple item)", "runtime", lambda s: node(s, "story.saving-steps")["content"]["steps"][2].update(body=long_text(40)), "MAX_WORDS"),
]


def _route_mismatch(s):
    # Only one template/route exists, so simulate a second template bound elsewhere by
    # pointing the spec at a route the schema allows but the template does not.
    sv.ctx().templates["__adversarial.other"] = {"id": "__adversarial.other", "routes": ["/other"], "nodes": []}
    s["template"] = "__adversarial.other"


def _generated_clean(s):
    """Turn the example into a compliant generated page (placeholder marks, generic tag icons, neutral copy)."""
    s["purpose"] = "generated"
    s["meta"]["iconSet"]["assetRole"] = "brand.placeholder-mark"
    s["meta"]["title"] = "Keep: everything you saved, findable."
    for n in s["nodes"]:
        c = n["content"]
        for key in ("logo", "topBarLogo"):
            if key in c:
                c[key]["assetRole"] = "brand.placeholder-mark"
        if "tapMarkRole" in c:
            c["tapMarkRole"] = "brand.placeholder-mark"
        if n["section"] == "story.why-funnel":
            for t in c["tags"]:
                t["iconRole"] = "icon.source-generic"
    # neutral copy where the real brand name appears
    def scrub(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and k not in sv.ROLE_KEYS:
                    o[k] = v.replace("savetoshelf.com", "example.com").replace("Shelf", "Keep").replace("shelf", "library")
                else:
                    scrub(v)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                if isinstance(v, str):
                    o[i] = v.replace("Shelf", "Keep").replace("shelf", "library")
                else:
                    scrub(v)
    scrub(s["nodes"])
    s["meta"]["description"] = s["meta"]["description"].replace("Shelf", "Keep")


def synth_for_template(t):
    """Generic per-template control: build a spec from the template's own node list,
    reusing the example's node bodies keyed by section (MASTER-GUIDE 3.22)."""
    bodies = {n["section"]: n for n in EXAMPLE["nodes"]}
    s = copy.deepcopy(EXAMPLE)
    s["template"] = t["id"]
    s["route"] = t["routes"][0]
    s["nodes"] = [copy.deepcopy(bodies[n["section"]]) for n in t["nodes"]]
    return s


def run():
    fails = []
    passed = 0
    counts = {"schema": 0, "structural": 0, "runtime": 0, "both": 0}
    for name, layer, mut, rule in MUTATIONS:
        sv._CTX = None  # fresh context (T16 patches templates in memory)
        s = copy.deepcopy(EXAMPLE)
        mut(s)
        schema_errs = list(SCHEMA_V.iter_errors(s))
        errors, _ = sv.validate(s)
        rules = {r for r, _ in errors}
        ok = rule in rules
        if layer in ("schema", "both"):
            ok = ok and bool(schema_errs)
        else:
            # structural/runtime mutations must get past the schema so we know the
            # SEMANTIC layer is what caught them (not an incidental schema error)
            ok = ok and not schema_errs
        counts[layer] += 1
        if ok:
            passed += 1
            print("REJECTED  %-72s [%s]" % (name, rule))
        else:
            fails.append(name)
            print("NOT CAUGHT %-71s expected %s, got %s (schema errs %d)" % (name, rule, sorted(rules), len(schema_errs)))
    sv._CTX = None

    controls = []
    controls.append(("C01 unmutated example", copy.deepcopy(EXAMPLE)))
    for tid, t in TEMPLATES.items():
        controls.append(("C02 synthesized control for %s" % tid, synth_for_template(t)))
    g = copy.deepcopy(EXAMPLE)
    _generated_clean(g)
    controls.append(("C03 compliant generated page (placeholder marks, generic icons)", g))
    cpass = 0
    for name, s in controls:
        errors, warnings = sv.validate(s)
        if errors:
            fails.append(name)
            print("CONTROL FAIL %-68s %s" % (name, errors[:3]))
        else:
            cpass += 1
            print("CONTROL OK  %-70s (%d warnings)" % (name, len(warnings)))

    # rhythm-rule exception works both directions (direct, synthetic sequences)
    c = sv.ctx()
    r1 = sv.Report(c)
    sv.check_rhythm({"nodes": [{"section": "story.finding"}, {"section": "story.saving-steps"}]}, r1)
    r2 = sv.Report(c)
    sv.check_rhythm({"nodes": [{"section": "story.saving-steps"}, {"section": "story.finding"}]}, r2)
    if not r1.warnings and any(w[0] == "NO_ADJACENT_SAME_CATEGORY" for w in r2.warnings):
        cpass += 1
        print("CONTROL OK  C04 named rhythm exception: excepted pair silent, reversed pair warns")
    else:
        fails.append("C04 rhythm exception")
        print("CONTROL FAIL C04 rhythm exception", r1.warnings, r2.warnings)

    total_m = len(MUTATIONS)
    print("\nmutations rejected: %d/%d (schema %d, structural %d, runtime %d, schema+semantic %d)" % (passed, total_m, counts["schema"], counts["structural"], counts["runtime"], counts["both"]))
    print("controls passed:    %d/%d" % (cpass, len(controls) + 1))
    print("RESULT: %s" % ("PASS" if not fails else "FAIL: " + ", ".join(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(run())
