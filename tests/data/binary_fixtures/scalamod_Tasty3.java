// Scala-3-shaped classfiles written with ASM (groovyjarjarasm, bundled in groovy-4.0.12.jar) -- no lib code.
// Hello.class = static forwarder (+ TASTY attribute, 16-byte UUID), Hello$.class = module (MODULE$, logic).
import groovyjarjarasm.asm.*;
import java.nio.file.*;
public class scalamod_Tasty3 implements Opcodes {
    static class Raw extends Attribute {
        byte[] b; Raw(String t, byte[] b) { super(t); this.b = b; }
        protected ByteVector write(ClassWriter cw, byte[] c, int l, int s, int x) { return new ByteVector().putByteArray(b, 0, b.length); }
    }
    public static void main(String[] a) throws Exception {
        Path out = Paths.get(a[0]);
        ClassWriter f = new ClassWriter(ClassWriter.COMPUTE_FRAMES | ClassWriter.COMPUTE_MAXS);
        f.visit(V1_8, ACC_PUBLIC | ACC_FINAL | ACC_SUPER, "Hello", null, "java/lang/Object", null);
        f.visitSource("Hello.scala", null);
        f.visitAttribute(new Raw("TASTY", new byte[]{1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16}));
        for (String[] m : new String[][]{{"main", "([Ljava/lang/String;)V"}, {"decodeConfig", "()Ljava/lang/String;"}}) {
            MethodVisitor mv = f.visitMethod(ACC_PUBLIC | ACC_STATIC, m[0], m[1], null, null);
            mv.visitCode();
            mv.visitFieldInsn(GETSTATIC, "Hello$", "MODULE$", "LHello$;");
            if (m[0].equals("main")) mv.visitVarInsn(ALOAD, 0);
            mv.visitMethodInsn(INVOKEVIRTUAL, "Hello$", m[0], m[1], false);
            mv.visitInsn(m[0].equals("main") ? RETURN : ARETURN);
            mv.visitMaxs(0, 0); mv.visitEnd();
        }
        f.visitEnd();
        Files.write(out.resolve("Hello.class"), f.toByteArray());
        ClassWriter c = new ClassWriter(ClassWriter.COMPUTE_FRAMES | ClassWriter.COMPUTE_MAXS);
        c.visit(V1_8, ACC_PUBLIC | ACC_FINAL | ACC_SUPER, "Hello$", null, "java/lang/Object", new String[]{"java/io/Serializable"});
        c.visitSource("Hello.scala", null);
        c.visitField(ACC_PUBLIC | ACC_STATIC | ACC_FINAL, "MODULE$", "LHello$;", null, null).visitEnd();
        MethodVisitor mv = c.visitMethod(ACC_STATIC, "<clinit>", "()V", null, null);
        mv.visitCode(); mv.visitTypeInsn(NEW, "Hello$"); mv.visitInsn(DUP);
        mv.visitMethodInsn(INVOKESPECIAL, "Hello$", "<init>", "()V", false);
        mv.visitFieldInsn(PUTSTATIC, "Hello$", "MODULE$", "LHello$;"); mv.visitInsn(RETURN); mv.visitMaxs(0, 0); mv.visitEnd();
        mv = c.visitMethod(ACC_PRIVATE, "<init>", "()V", null, null);
        mv.visitCode(); mv.visitVarInsn(ALOAD, 0); mv.visitMethodInsn(INVOKESPECIAL, "java/lang/Object", "<init>", "()V", false);
        mv.visitInsn(RETURN); mv.visitMaxs(0, 0); mv.visitEnd();
        mv = c.visitMethod(ACC_PRIVATE, "writeReplace", "()Ljava/lang/Object;", null, null);
        mv.visitCode(); mv.visitInsn(ACONST_NULL); mv.visitInsn(ARETURN); mv.visitMaxs(0, 0); mv.visitEnd();
        mv = c.visitMethod(ACC_PUBLIC, "decodeConfig", "()Ljava/lang/String;", null, null);
        mv.visitCode(); mv.visitLdcInsn("SEhDRgEAAAA="); mv.visitInsn(ARETURN); mv.visitMaxs(0, 0); mv.visitEnd();
        mv = c.visitMethod(ACC_PUBLIC, "main", "([Ljava/lang/String;)V", null, null);
        mv.visitCode(); mv.visitInsn(RETURN); mv.visitMaxs(0, 0); mv.visitEnd();
        c.visitEnd();
        Files.write(out.resolve("Hello$.class"), c.toByteArray());
        Files.write(out.resolve("Hello.tasty"), new byte[]{0x5c, (byte) 0xa1, (byte) 0xab, 0x1f, 28, 3, 0});   // TASTy magic 5CA1AB1F
    }
}
