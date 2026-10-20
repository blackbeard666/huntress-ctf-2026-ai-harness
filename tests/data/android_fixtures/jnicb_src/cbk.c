/* JNI native that calls BACK into Java by name (coverage atlas row 82): FindClass + GetStaticMethodID +
   NewStringUTF literal arg(s) + CallStaticObjectMethod; the Java method computes the answer from the native's args. */
#include <jni.h>

JNIEXPORT jstring JNICALL Java_com_huntress_mobile_d21_Bridge_nativeAnswer(JNIEnv *env, jclass self) {
    jclass k = (*env)->FindClass(env, CB_CLASS);
    if (!k) return NULL;
    jmethodID m = (*env)->GetStaticMethodID(env, k, CB_NAME, CB_SIG);
    if (!m) return NULL;
    jstring a = (*env)->NewStringUTF(env, CB_ARG1);
#ifdef CB_ARG2
    jstring b = (*env)->NewStringUTF(env, CB_ARG2);
    return (jstring)(*env)->CallStaticObjectMethod(env, k, m, a, b);
#else
    return (jstring)(*env)->CallStaticObjectMethod(env, k, m, a);
#endif
}
