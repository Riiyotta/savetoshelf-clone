#!/usr/bin/env python3
"""Prove that verify_all.py's drift checks actually FAIL on injected drift.

Usage: python3 extraction/prove_drift.py [--evidence-root DIR]

Copies design-repo/ into a fresh temp dir per case, injects one defect, runs
verify_all.py there (pointing --evidence-root at the real project when it is
available) and asserts a non-zero exit with the expected check name in the
output. Finally asserts the untouched real repo still passes.
Citation-drift cases need a real evidence root; in a standalone copy they are
reported as SKIPPED (not silently passed).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def jdump(p, o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, indent=2, ensure_ascii=False)


def m_phantom(d):
    p = os.path.join(d, "tokens/llm/component-allowlist.json")
    o = jload(p)
    o["sections"].append("hero.phantom")
    jdump(p, o)


def m_orphan(d):
    shutil.copy(os.path.join(d, "primitives/caret.json"), os.path.join(d, "primitives/caret-copy.json"))
    p = os.path.join(d, "primitives/caret-copy.json")
    o = jload(p)
    o["id"] = "primitive.caret-copy"
    jdump(p, o)


def m_cite_range(d):
    p = os.path.join(d, "sections/support.faq.json")
    o = jload(p)
    o["measuredFrom"][0]["cite"] = "src/components/Faq.jsx:80-999"
    jdump(p, o)


def m_cite_wrong_content(d):
    p = os.path.join(d, "sections/support.faq.json")
    o = jload(p)
    o["measuredFrom"][0]["cite"] = "src/components/Faq.jsx:1-5"  # in range, wrong code
    jdump(p, o)


def m_count(d):
    p = os.path.join(d, "registry.manifest.json")
    o = jload(p)
    o["counts"]["sections"] += 1
    jdump(p, o)


def m_allowlist_version(d):
    p = os.path.join(d, "tokens/llm/component-allowlist.json")
    o = jload(p)
    o["version"] = "9.9.9"
    jdump(p, o)


def m_pinned(d):
    p = os.path.join(d, "assets/asset-roles.json")
    o = jload(p)
    for r in o["roles"]:
        if r["id"] == "form.waitlist-endpoint":
            r["generationPolicy"] = "may-generate-new"  # valid enum member, wrong pinned value
    o["pinned"]["form.waitlist-endpoint"] = "may-generate-new"
    jdump(p, o)


def m_abs_path(d):
    p = os.path.join(d, "README.md")
    with open(p, "a", encoding="utf-8") as f:
        f.write("\nsource: " + "/" + "Users" + "/someone/project\n")


def m_graph_rule(d):
    p = os.path.join(d, "compatibility/graph.json")
    o = jload(p)
    o["rules"].append({"id": "UNIMPLEMENTED_RULE", "severity": "error", "rule": "x", "exceptions": [], "enforcedBy": "semantic_validate.nope", "checkedAgainstTemplates": "n/a"})
    jdump(p, o)


def m_entry_outside(d):
    p = os.path.join(d, "registry.manifest.json")
    o = jload(p)
    o["entryPoints"]["cloneSpec"] = "../CLONE_SPEC.md"
    jdump(p, o)


def m_schema_contract(d):
    p = os.path.join(d, "sections/story.why-funnel.json")
    o = jload(p)
    o["motionSchema"]["properties"]["reducedMotionFallback"]["const"] = "static-no-motion"
    jdump(p, o)


CASES = [
    ("phantom allowlist entry", m_phantom, "allowlist-parity", False),
    ("orphan contract file", m_orphan, "allowlist-parity", False),
    ("out-of-range citation", m_cite_range, "citations", True),
    ("in-range citation, wrong content", m_cite_wrong_content, "citations", True),
    ("wrong manifest count", m_count, "manifest-counts", False),
    ("allowlistVersion drift", m_allowlist_version, "allowlist-version", False),
    ("pinned endpoint policy -> valid-but-wrong value", m_pinned, "asset-roles-pinned", False),
    ("absolute local path", m_abs_path, "abs-path", False),
    ("graph rule with no validator implementation", m_graph_rule, "graph-validator-parity", False),
    ("entryPoint outside package", m_entry_outside, "entry-points", False),
    ("section motion const drifts from schema", m_schema_contract, "schema-contract-parity", False),
]


def run_verify(repo_dir, root):
    cmd = [sys.executable, os.path.join(repo_dir, "extraction", "verify_all.py")]
    if root:
        cmd += ["--evidence-root", root]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main(argv):
    root = argv[argv.index("--evidence-root") + 1] if "--evidence-root" in argv else os.path.abspath(os.path.join(REPO, ".."))
    has_root = os.path.isfile(os.path.join(root, "CLONE_SPEC.md"))
    bad = 0
    for name, mut, check, needs_root in CASES:
        if needs_root and not has_root:
            print("SKIPPED  %-52s (needs the sibling evidence tree)" % name)
            continue
        tmp = tempfile.mkdtemp(prefix="drift-")
        d = os.path.join(tmp, "design-repo")
        shutil.copytree(REPO, d, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
        try:
            mut(d)
            code, out = run_verify(d, root if has_root else None)
            caught = code != 0 and ("FAIL [%s]" % check) in out
            print("%s %-52s -> exit %d, [%s] %s" % ("CAUGHT  " if caught else "MISSED  ", name, code, check, "reported" if caught else "NOT reported"))
            bad += 0 if caught else 1
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    code, out = run_verify(REPO, root if has_root else None)
    print("real repo verify_all exit %d (%s)" % (code, "PASS" if code == 0 else "FAIL"))
    if code != 0:
        bad += 1
    print("prove_drift: %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
