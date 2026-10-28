/*
 * Copyright 2026 Dukehoff GmbH
 * SPDX-License-Identifier: Apache-2.0
 */
package com.dukehoff.netbeans.lombok;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import java.io.File;
import java.net.URL;
import org.junit.Test;
import org.openide.filesystems.FileUtil;

public class LombokProcessorPathTest {

    @Test
    public void readsTheVersionFromTheJarName() throws Exception {
        assertArrayEquals(new int[] {1, 18, 38}, LombokProcessorPath.lombokVersion(root("lombok-1.18.38.jar")));
        assertNull(LombokProcessorPath.lombokVersion(root("lombok-mapstruct-binding-0.2.0.jar")));
        assertNull(LombokProcessorPath.lombokVersion(root("guava-33.0.jar")));
    }

    @Test
    public void comparesVersions() {
        assertTrue(LombokProcessorPath.older(new int[] {1, 18, 46}, new int[] {1, 18, 48}));
        assertFalse(LombokProcessorPath.older(new int[] {1, 18, 48}, new int[] {1, 18, 48}));
        assertFalse(LombokProcessorPath.older(new int[] {1, 19, 0}, new int[] {1, 18, 48}));
    }

    private static URL root(String jarName) throws Exception {
        return FileUtil.getArchiveRoot(new File("/repo/" + jarName).toURI().toURL());
    }
}
