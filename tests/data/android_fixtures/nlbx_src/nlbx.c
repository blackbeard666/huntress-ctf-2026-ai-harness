/* JNI natives the Dalvik chain calls mid-way (coverage atlas rows 37, 96 / target dex-eval-native-bridge).
   NLBX_CLS = mangled class ("com_huntress_mobile_d24_Native_1Secrets"); NLBX_REGNAT: no Java_* exports, the methods
   are bound by a RegisterNatives table in JNI_OnLoad. */
#include <jni.h>
#include <stdio.h>
#include <stdint.h>

#define CAT2(a, b) a##b
#define CAT(a, b) CAT2(a, b)

static jlong mixl(jlong a, jint b) {
    uint64_t x = (uint64_t)a + 0x9E3779B97F4A7C15ULL;
    x ^= (uint64_t)(uint32_t)b * 0x10001ULL;
    x *= 0xBF58476D1CE4E5B9ULL;
    return (jlong)((x << 13) | (x >> 51));
}

#ifndef NLBX_REGNAT
JNIEXPORT jlong JNICALL CAT(CAT(Java_, NLBX_CLS), _mix__JI)(JNIEnv *env, jclass c, jlong a, jint b) { return mixl(a, b); }
JNIEXPORT jint JNICALL CAT(CAT(Java_, NLBX_CLS), _mix__I)(JNIEnv *env, jclass c, jint a) { return a * 31 + 7; }
JNIEXPORT jstring JNICALL CAT(CAT(Java_, NLBX_CLS), _tag)(JNIEnv *env, jobject self, jstring pre, jlong v) {
    const char *p = (*env)->GetStringUTFChars(env, pre, 0);
    char buf[64];
    if (!p) return NULL;
    snprintf(buf, sizeof buf, "%s%016llX", p, (unsigned long long)v);
    (*env)->ReleaseStringUTFChars(env, pre, p);
    return (*env)->NewStringUTF(env, buf);
}
#else
static jlong fold(JNIEnv *env, jclass c, jlong a, jlong b) { return mixl(a ^ b, (jint)(b >> 7)); }
static jint salt(JNIEnv *env, jclass c, jint x) { return (x ^ 0x5A5A) * 0x2F + 3; }
static const JNINativeMethod METHODS[] = {
    {"fold", "(JJ)J", (void *)fold},
    {"salt", "(I)I", (void *)salt},
};
JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *reserved) {
    JNIEnv *env;
    if ((*vm)->GetEnv(vm, (void **)&env, JNI_VERSION_1_6) != JNI_OK) return -1;
    jclass k = (*env)->FindClass(env, NLBX_JCLS);
    if (!k || (*env)->RegisterNatives(env, k, METHODS, 2) != 0) return -1;
    return JNI_VERSION_1_6;
}
#endif
