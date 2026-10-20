public class Decoy {
    public static void main(String[] a) {
        StringBuilder sb = new StringBuilder();
        sb.append("=0jd");
        String descriptor_deadc0de = sb.reverse().toString();
        System.out.print(new String(java.util.Base64.getDecoder().decode(descriptor_deadc0de)));
    }
}
