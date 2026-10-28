/*
 * Copyright 2026 Dukehoff GmbH
 * SPDX-License-Identifier: Apache-2.0
 */
package demo;

public class Main {
    public static void main(String[] args) {
        Person p = Person.builder().name("Ada").age(36).build();
        p.setAge(37);
        System.out.println(p.getName() + " is " + p.getAge());
    }
}
