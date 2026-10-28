<!--

    Copyright 2026 Dukehoff GmbH
    SPDX-License-Identifier: Apache-2.0

-->
# Contributing to Lombok for nb-javac

Thanks for your interest. Reports help most with the NetBeans version, the project's Lombok version and,
if possible, a small project that shows the problem (like `demo/`). Pull requests are welcome too.

## Contributor license agreement

Before we can merge your first pull request, you sign a contributor license agreement (CLA) with
Dukehoff GmbH, based on the standard [Harmony agreements](https://www.harmonyagreements.org/): the
[individual](https://github.com/dukehoff-gmbh/cla/blob/main/individual-cla.md) or, for work done for
an employer, the [entity](https://github.com/dukehoff-gmbh/cla/blob/main/entity-cla.md) agreement
(details in [dukehoff-gmbh/cla](https://github.com/dukehoff-gmbh/cla)).

- **You keep the copyright** of your contribution and may use it as you like. You grant Dukehoff GmbH
  a non-exclusive license to distribute it, also under other licenses than the Apache License 2.0;
  in return, your contribution always stays available under the Apache License 2.0.
- **One signature covers all projects** of Dukehoff GmbH.
- **Signing:** on your first pull request a bot comments with the link to the agreement. Read it, then
  post the sentence the bot names as a comment; `recheck` checks again.
- **Work done for an employer:** your employer signs the entity version first (an authorized
  signatory, by email to opensource@dukehoff.com); we then add you.
- **Your data:** we keep your GitHub login and id, the pull request and the time of signing, in a
  private repository of Dukehoff GmbH, as the record of the agreement, for as long as we distribute
  your contribution.

## Building and testing

You need a JDK 17 or newer and Maven: `mvn clean package` builds `target/lombok-nb-javac-<version>.nbm`
and runs the unit tests. To check the plugin, install the NBM into a NetBeans 31 with a fresh user
directory (`netbeans --userdir <dir>`), open `demo/` and look at `demo/src/main/java/demo/Main.java`
before and after the restart.

## Rules for code

- Java 17, no compiler warnings (`-Xlint:all` minus serial and processing); match the existing style.
- Only public NetBeans APIs, from Maven Central at the release set in `pom.xml`.
- Every file carries the license header (`Copyright 2026 Dukehoff GmbH`,
  `SPDX-License-Identifier: Apache-2.0`). The build checks it (`license-maven-plugin`, in `validate`);
  `mvn license:format` adds it to new files.
- Small, focused commits with a message that says why.

## Releasing (maintainers)

A tag `v<version>` on `main` (e.g. `git tag -s v1.0.0 && git push origin v1.0.0`) starts the Release
workflow: it builds that version (the pom stays at its `-SNAPSHOT` version in the repository) and
publishes a GitHub release with `lombok-nb-javac-<version>.nbm` and `SHA256SUMS`. Versions with a suffix
(`1.1.0-rc1`) become pre-releases. Actions > Release > Run workflow is a dry run of the same steps.

A tag also puts the plugin on Maven Central (`com.dukehoff.netbeans:lombok-nb-javac`), where the NetBeans
Plugin Portal takes it from. That needs the secrets `CENTRAL_USERNAME` and `CENTRAL_PASSWORD` (a user
token of the Central Portal account that owns the namespace `com.dukehoff`) and `MAVEN_GPG_PRIVATE_KEY`
and `MAVEN_GPG_PASSPHRASE` (the release signing key); without them the step is skipped. The upload waits
in the Central Portal for **Publish** unless the repository variable `CENTRAL_AUTO_PUBLISH` is `true`. To
check the bundle locally: `mvn -P central deploy -DskipTests -Dcentral.skipUpload=true` with a release
version (the bundle is in `target/central-publishing`).
