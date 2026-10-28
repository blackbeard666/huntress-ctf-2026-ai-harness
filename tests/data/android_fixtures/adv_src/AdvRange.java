import org.apache.maven.artifact.versioning.*;
public class AdvRange { public static void main(String[] a) throws Exception {
  System.out.println(VersionRange.createFromVersionSpec(a[1]).containsVersion(new DefaultArtifactVersion(a[0]))); } }
