package com.huntress.mobile.d28.slip;

import java.io.*;
import java.nio.file.Files;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Vulnerable unzip helper (zip slip): no canonical-path check before writing each entry. On Android the app calls
 *  unpack(getAssets().open("bundle.zip"), new File(getFilesDir(), "unpacked")) then readConfig(getFilesDir()) /
 *  pluginDex(getCodeCacheDir()). main() runs the same code on a desktop JVM (the fixture oracle). */
public final class Loader {
  static final String ASSET = "bundle.zip", DIR = "unpacked", CONFIG = "config.json", PLUGIN = "plugin.dex";

  public static void unpack(InputStream in, File dir) throws IOException {
    try (ZipInputStream zin = new ZipInputStream(in)) {
      ZipEntry e;
      byte[] buf = new byte[8192];
      while ((e = zin.getNextEntry()) != null) {
        File out = new File(dir, e.getName());
        if (e.isDirectory()) { out.mkdirs(); continue; }
        out.getCanonicalFile().getParentFile().mkdirs();
        try (FileOutputStream fo = new FileOutputStream(out)) {
          int n;
          while ((n = zin.read(buf)) > 0) fo.write(buf, 0, n);
        }
      }
    }
  }

  public static byte[] readConfig(File filesDir) throws IOException {
    return Files.readAllBytes(new File(filesDir, CONFIG).toPath());
  }

  public static byte[] pluginDex(File codeCacheDir) throws IOException {
    return Files.readAllBytes(new File(codeCacheDir, PLUGIN).toPath());
  }

  /** java Loader <asset.zip> <app data dir> <config|plugin>: extract under <data>/files/unpacked, print what the app reads. */
  public static void main(String[] a) throws IOException {
    File data = new File(a[1]), files = new File(data, "files");
    new File(files, DIR).mkdirs();
    new File(data, "code_cache").mkdirs();
    try {
      unpack(new FileInputStream(a[0]), new File(files, DIR));
    } catch (IOException e) {
      System.err.println("unpack stopped: " + e.getMessage());  // the app logs and goes on with what was written
    }
    System.out.write(a[2].equals("plugin") ? pluginDex(new File(data, "code_cache")) : readConfig(files));
    System.out.flush();
  }
}
