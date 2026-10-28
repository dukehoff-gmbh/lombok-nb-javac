#!/usr/bin/env python3
#
# Copyright 2026 Dukehoff GmbH
# SPDX-License-Identifier: Apache-2.0
#

"""Which Lombok versions work with which nb-javac (the javac NetBeans parses with).

Compiles demo/ with nb-javac, with Lombok on the class path and the processor path, as NetBeans does, and
checks that Lombok generated the builder. nb-javac runs from the class path (like inside NetBeans), so the
JDK's own compiler modules are left out with --limit-modules.

  check.py                                  nb-javac of NetBeans' master branch, of open NetBeans pull
                                            requests that move to a newer nb-javac and the newest on Maven
                                            Central, against
                                            the bundled Lombok and the newest Lombok releases
  check.py --nb-javac jdk-27+26 --lombok 1.18.46,1.18.48

Prints a Markdown table (also to --markdown FILE). Exit 1 if the bundled Lombok (lombok.version in
pom.xml) fails with NetBeans' master nb-javac, or with the --nb-javac given. Needs a JDK 17 or newer
(JAVA_HOME or java on the PATH); GITHUB_TOKEN, if set, is used for GitHub's API.
"""
import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENTRAL = "https://repo1.maven.org/maven2"
NETBEANS = "apache/netbeans"
BINARIES_LIST = "java/libs.nbjavacapi/external/binaries-list"
NEWEST_LOMBOKS = 4


def fetch(url, accept=None):
    req = urllib.request.Request(url, headers={"User-Agent": "lombok-nb-javac-compat"})
    if accept:
        req.add_header("Accept", accept)
    if url.startswith("https://api.github.com/") and os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def github(path):
    return json.loads(fetch("https://api.github.com/" + path, "application/vnd.github+json"))


def central_versions(group, artifact):
    meta = ET.fromstring(fetch(f"{CENTRAL}/{group.replace('.', '/')}/{artifact}/maven-metadata.xml"))
    return [v.text for v in meta.iter("version")]


def artifact(cache, group, name, version, classifier=None):
    file = f"{name}-{version}{'-' + classifier if classifier else ''}.jar"
    path = os.path.join(cache, group, name, version, file)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = fetch(f"{CENTRAL}/{group.replace('.', '/')}/{name}/{version}/{file}")
        with open(path + ".part", "wb") as f:
            f.write(data)
        os.replace(path + ".part", path)
    return path


def lombok_key(v):
    return tuple(int(x) for x in v.split("."))


def nbjavac_key(v):
    m = re.fullmatch(r"jdk-(\d+)(?:\+(\d+))?", v)
    return (int(m.group(1)), int(m.group(2) or 1000)) if m else None


def bundled_lombok():
    pom = ET.parse(os.path.join(ROOT, "pom.xml")).getroot()
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    return pom.find("m:properties/m:lombok.version", ns).text


def nbjavac_in(binaries_list):
    m = re.search(r"com\.dukescript\.nbjavac:nb-javac:([^:\s]+)\s", binaries_list + "\n")
    return m.group(1) if m else None


def tracked_nbjavacs():
    """[(nb-javac version, where it comes from)]: NetBeans' master first."""
    found = []
    content = github(f"repos/{NETBEANS}/contents/{BINARIES_LIST}?ref=master")["content"]
    found.append((nbjavac_in(base64.b64decode(content).decode()), "NetBeans master"))
    query = urllib.parse.quote(f"repo:{NETBEANS} is:pr is:open nb-javac in:title")
    for pr in github(f"search/issues?q={query}&per_page=20")["items"]:
        head = github(f"repos/{NETBEANS}/pulls/{pr['number']}")["head"]
        try:
            text = fetch(f"https://raw.githubusercontent.com/{head['repo']['full_name']}/{head['sha']}/{BINARIES_LIST}")
        except Exception:
            continue
        version = nbjavac_in(text.decode())
        # only pull requests that move to a newer nb-javac (old abandoned ones stay open for years)
        if version and nbjavac_key(version) and nbjavac_key(version) > nbjavac_key(found[0][0]):
            found.append((version, f"NetBeans PR [#{pr['number']}]({pr['html_url']})"))
    newest = max((v for v in central_versions("com.dukescript.nbjavac", "nb-javac") if nbjavac_key(v)), key=nbjavac_key)
    found.append((newest, "newest on Maven Central"))
    seen, result = set(), []
    for v, where in found:
        if v and v not in seen:
            seen.add(v)
            result.append((v, where))
        elif v:
            result = [(x, w + ", " + where if x == v else w) for x, w in result]
    return result


def java():
    home = os.environ.get("JAVA_HOME")
    return os.path.join(home, "bin", "java") if home else shutil.which("java")


def check(cache, nbjavac, lombok):
    """(True, "") if Lombok generated the builder, else (False, the first error)."""
    javac = [artifact(cache, "com.dukescript.nbjavac", "nb-javac", nbjavac, "api"),
             artifact(cache, "com.dukescript.nbjavac", "nb-javac", nbjavac)]
    jar = artifact(cache, "org.projectlombok", "lombok", lombok)
    sources = os.path.join(ROOT, "demo", "src", "main", "java", "demo")
    with tempfile.TemporaryDirectory() as out:
        r = subprocess.run([java(), "-Duser.language=en", "-Duser.country=US",
                            "--limit-modules", "java.base,java.logging,java.xml,jdk.unsupported,jdk.zipfs",
                            "-cp", os.pathsep.join(javac), "com.sun.tools.javac.Main",
                            "-nowarn", "-source", "17", "-target", "17",
                            "-cp", jar, "-processorpath", jar, "-d", out]
                           + [os.path.join(sources, f) for f in sorted(os.listdir(sources))],
                           capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(os.path.join(out, "demo", "Person$PersonBuilder.class")):
            return True, ""
        lines = [l.strip() for l in (r.stderr + r.stdout).splitlines()
                 if re.search(r"error|Exception|Error:", l) and "[options]" not in l]
        cause = [l for l in lines if l.startswith("Caused by")]
        return False, (cause or lines or ["no builder generated"])[-1 if cause else 0][:160]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--nb-javac", help="comma-separated nb-javac versions (default: the tracked ones)")
    ap.add_argument("--lombok", help="comma-separated Lombok versions (default: bundled and newest releases)")
    ap.add_argument("--markdown", help="also write the table to this file")
    ap.add_argument("--cache", default=os.path.join(tempfile.gettempdir(), "lombok-nb-javac-compat"))
    args = ap.parse_args()

    bundled = bundled_lombok()
    if args.nb_javac:
        nbjavacs = [(v, "given") for v in args.nb_javac.split(",")]
        gate = {v for v, _ in nbjavacs}
    else:
        nbjavacs = tracked_nbjavacs()
        gate = {nbjavacs[0][0]}
    if args.lombok:
        lomboks = args.lombok.split(",")
    else:
        releases = [v for v in central_versions("org.projectlombok", "lombok") if re.fullmatch(r"\d+\.\d+\.\d+", v)]
        lomboks = sorted(set(sorted(releases, key=lombok_key)[-NEWEST_LOMBOKS:]) | {bundled}, key=lombok_key)

    rows, failed = [], False
    for nbjavac, where in nbjavacs:
        for lombok in reversed(lomboks):
            ok, why = check(args.cache, nbjavac, lombok)
            label = lombok + (" (bundled)" if lombok == bundled else "")
            rows.append(f"| {nbjavac} | {where} | {label} | {'works' if ok else 'fails: `' + why + '`'} |")
            if not ok and lombok == bundled and nbjavac in gate:
                failed = True
    table = "\n".join(["| nb-javac | used by | Lombok | result |", "|---|---|---|---|"] + rows) + "\n"
    print(table)
    if args.markdown:
        with open(args.markdown, "w") as f:
            f.write(table)
    if failed:
        print(f"The bundled Lombok {bundled} fails with {', '.join(sorted(gate))}.", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
