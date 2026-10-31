<!--

    Copyright 2026 Dukehoff GmbH
    SPDX-License-Identifier: Apache-2.0

-->
# Lombok in NetBeans 31: a minimal demo

NetBeans 31 parses Java with nb-javac 27 (the javac of JDK 27). Lombok supports that javac only from
1.18.48 (2026-09-01); 1.18.46 and older generate nothing inside the IDE. This project uses 1.18.46.

1. `mvn package && java -cp target/classes demo.Main` builds and prints `Ada is 37`: the build is fine.
2. Open the project in NetBeans 31 and open `Main.java`: `builder()`, `setAge` and `getName` are marked
   as errors ("cannot find symbol").
3. Install the plugin **Lombok for nb-javac** (Tools > Plugins > Available Plugins) and restart NetBeans when the
   installer asks (projects open at install time keep their processor path until then). `Main.java`
   shows no errors. The plugin bundles Lombok 1.18.48 and uses it inside the IDE in place of an older Lombok
   on a project's annotation processor path; the build and the project files are not changed.

Without the plugin, raising `lombok.version` in `pom.xml` to 1.18.48 has the same effect.
