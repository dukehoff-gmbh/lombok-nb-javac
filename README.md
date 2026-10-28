<!--

    Copyright 2026 Dukehoff GmbH
    SPDX-License-Identifier: Apache-2.0

-->
# Lombok for nb-javac

A NetBeans plugin for projects whose Lombok is older than the javac NetBeans parses with.

NetBeans analyzes Java with nb-javac, the javac of a recent JDK, independent of the JDK a project builds
with. Lombok hooks into javac and supports each javac version only from a certain release on: NetBeans 31
parses with the javac of JDK 27, which Lombok supports from 1.18.48 (2026-09-01). With Lombok 1.18.46 or
older, Maven and Gradle builds are fine, but in the editor Lombok generates nothing: getters, setters,
builders and constructors are missing, so the editor shows false "cannot find symbol" errors, and
navigation and refactorings do not see the generated members.

This plugin bundles a current Lombok and uses it inside the IDE in place of an older Lombok on a project's
annotation processor path. The project's build, its `pom.xml` or `build.gradle` and its dependencies are
not changed. A project that already uses a current Lombok is left as it is.

## Try it

[`demo/`](demo/) is a small Maven project with Lombok 1.18.46: it builds and runs, shows the errors in
NetBeans 31, and shows none once the plugin is installed. See [demo/README.md](demo/README.md).

## Install

1. Download `lombok-nb-javac-<version>.nbm` from the [releases](https://github.com/dukehoff-gmbh/lombok-nb-javac/releases).
2. In NetBeans: Tools > Plugins > Downloaded > Add Plugins..., choose the file, Install.
3. Restart NetBeans when the installer asks: projects that are already open keep their processor path
   until then.

Requires NetBeans 31.

## Build

```sh
mvn clean package        # target/lombok-nb-javac-<version>.nbm, with the unit tests
```

The Lombok version inside the plugin is `lombok.version` in `pom.xml`. When NetBeans moves to a newer
nb-javac, the plugin needs a Lombok release that supports that javac.

## Compatibility

`compat/check.py` compiles `demo/` with a given nb-javac and Lombok, the way NetBeans runs them:

```sh
python3 compat/check.py --nb-javac jdk-27+26 --lombok 1.18.46,1.18.48
```

| nb-javac | NetBeans | Lombok |
|---|---|---|
| jdk-27+26 | 31 | 1.18.48 works; 1.18.42 to 1.18.46 fail (`ClassNotFoundException: com.sun.tools.javac.tree.EndPosTable`) |
| jdk-26+35 | 30 | 1.18.44 and 1.18.46 work |

Without arguments it checks the nb-javac of NetBeans' master branch, of open NetBeans pull requests that
move to a newer nb-javac, and the newest nb-javac on Maven Central against the bundled and the newest Lombok
releases. A daily workflow runs it and keeps the result in the issue labeled `compatibility`, so a new
nb-javac that needs a newer Lombok shows up before the NetBeans release that brings it.

## License

Apache License 2.0 (`LICENSE`). The plugin bundles Project Lombok under the MIT License
(`LICENSE-lombok`); see `NOTICE`. Contributions need the contributor license agreement of Dukehoff GmbH
(see `CONTRIBUTING.md`).

Lombok for nb-javac started as part of [Dukehoff MCP for Java](https://github.com/dukehoff-gmbh/dukehoff-mcp)
and is developed here on its own. Written with AI assistance (Claude), reviewed and tested by Dukehoff GmbH.
