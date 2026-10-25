/* JNI natives that USE the JNIEnv inside a v2 chain (coverage atlas rows 37, 82, 96 / target
   native-bridge-jnienv-callbacks): GetStringUTFChars / ReleaseStringUTFChars on a jstring arg, GetArrayLength +
   GetByteArrayElements / ReleaseByteArrayElements and GetByteArrayRegion on a byte[] arg, FindClass +
   GetStaticFieldID + GetStaticLongField / GetStaticIntField (dex K constants), GetStaticMethodID +
   CallStaticLongMethod / ...V / ...A back into a dex mixer, NewStringUTF result.
   JE_CLS = mangled Java class, JE_K = the constants class FindClass looks up, JE_V = use CallStaticLongMethodV. */
#include <jni.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdint.h>

#define CAT2(a, b) a##b
#define CAT(a, b) CAT2(a, b)

static jlong callv(JNIEnv *env, jclass k, jmethodID m, ...) {
    va_list ap;
    va_start(ap, m);
    jlong r = (*env)->CallStaticLongMethodV(env, k, m, ap);
    va_end(ap);
    return r;
}

JNIEXPORT jlong JNICALL CAT(CAT(Java_, JE_CLS), _fold)(JNIEnv *env, jclass c, jstring tag, jbyteArray data, jint n) {
    const char *p = (*env)->GetStringUTFChars(env, tag, 0);
    if (!p) return 0;
    uint64_t h = 0xCBF29CE484222325ULL;
    for (const char *q = p; *q; q++) h = (h ^ (uint8_t)*q) * 0x100000001B3ULL;
    (*env)->ReleaseStringUTFChars(env, tag, p);
    jsize len = (*env)->GetArrayLength(env, data);
    jbyte *b = (*env)->GetByteArrayElements(env, data, 0);
    if (!b) return 0;
    for (jsize i = 0; i < len; i++) h = (h ^ (uint8_t)b[i]) * 0x100000001B3ULL;
    (*env)->ReleaseByteArrayElements(env, data, b, JNI_ABORT);
    jclass k = (*env)->FindClass(env, JE_K);
    if (!k) return 0;
    jfieldID f1 = (*env)->GetStaticFieldID(env, k, "K1", "J");
    jfieldID f2 = (*env)->GetStaticFieldID(env, k, "K2", "I");
    if (!f1 || !f2) return 0;
    h ^= (uint64_t)(*env)->GetStaticLongField(env, k, f1);
    h += (uint64_t)(uint32_t)(*env)->GetStaticIntField(env, k, f2);
    jmethodID m = (*env)->GetStaticMethodID(env, k, "mixer", "(JI)J");
    if (!m) return 0;
#ifdef JE_V
    return callv(env, k, m, (jlong)h, n);
#else
    return (*env)->CallStaticLongMethod(env, k, m, (jlong)h, n);
#endif
}

JNIEXPORT jstring JNICALL CAT(CAT(Java_, JE_CLS), _seal)(JNIEnv *env, jclass c, jlong v, jbyteArray salt) {
    jbyte s[4];
    (*env)->GetByteArrayRegion(env, salt, 0, 4, s);
    jclass k = (*env)->FindClass(env, JE_K);
    if (!k) return NULL;
    jmethodID m = (*env)->GetStaticMethodID(env, k, "mixer", "(JI)J");
    if (!m) return NULL;
    jvalue a[2];
    a[0].j = v;
    a[1].i = (jint)((uint32_t)(uint8_t)s[0] | (uint32_t)(uint8_t)s[1] << 8 | (uint32_t)(uint8_t)s[2] << 16 |
                    (uint32_t)(uint8_t)s[3] << 24);
    jlong r = (*env)->CallStaticLongMethodA(env, k, m, a);
    char buf[32];
    snprintf(buf, sizeof buf, "ANS-%016llX", (unsigned long long)r);
    return (*env)->NewStringUTF(env, buf);
}
