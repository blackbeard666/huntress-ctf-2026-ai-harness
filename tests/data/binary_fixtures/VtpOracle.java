// Independent oracle: load both fixture jars with a URLClassLoader, call the named method reflectively over the
// documented candidate order (String: null,"","a","A","0"," ","ab","abc","-1","abcd","abcdefgh"; int: 0,-1,1,2,MIN,MAX,
// then 0..64) and print the first input where A throws and B returns. usage: java VtpOracle.java A.jar B.jar Class.method
import java.lang.reflect.*; import java.net.*; import java.util.*;
public class VtpOracle {
  public static void main(String[] a) throws Exception {
    String[] cm = a[2].split("\\.");
    Method ma = find(a[0], cm[0].split("@")[0], cm[1]), mb = find(a[1], cm[0].contains("@") ? cm[0].split("@")[1] : cm[0], cm[1]);
    List<Object> cands = new ArrayList<>();
    if (ma.getParameterTypes()[0] == String.class) cands.addAll(Arrays.asList(null, "", "a", "A", "0", " ", "ab", "abc", "-1", "abcd", "abcdefgh"));
    else { cands.addAll(Arrays.asList(0, -1, 1, 2, Integer.MIN_VALUE, Integer.MAX_VALUE)); for (int k = 0; k <= 64; k++) cands.add(k); }
    for (Object c : cands) {
      String ra = run(ma, c), rb = run(mb, c);
      if (ra.startsWith("!") && !rb.startsWith("!")) { System.out.println("{\"trigger_input\": \"" + (c == null ? "null" : c instanceof String ? "\\\"" + c + "\\\"" : c) + "\", \"vulnerable_outcome\": \"" + ra.substring(1) + "\", \"corrected_result\": \"" + rb + "\"}"); return; }
    }
    System.out.println("{\"trigger_found\": \"false\"}");
  }
  static Method find(String jar, String cls, String m) throws Exception {
    Class<?> k = new URLClassLoader(new URL[]{new java.io.File(jar).toURI().toURL()}).loadClass(cls);
    for (Method x : k.getDeclaredMethods()) if (x.getName().equals(m)) return x;
    throw new RuntimeException("no method");
  }
  static String run(Method m, Object c) {
    try { Object recv = Modifier.isStatic(m.getModifiers()) ? null : m.getDeclaringClass().getDeclaredConstructor().newInstance();
      return String.valueOf(m.invoke(recv, c)); }
    catch (InvocationTargetException e) { return "!" + e.getCause().getClass().getName(); }
    catch (Exception e) { return "!?" + e; }
  }
}
