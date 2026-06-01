package org.pngquant;


import boundless.utility.NativeUtils;

abstract class LiqObject {
    // Whether the libimagequant native library loaded on this platform.
    // Only x86_64 (and legacy) binaries are shipped; there is no arm64/Apple
    // Silicon build, so on arm64 this stays false. We catch Throwable (not just
    // Exception) because a wrong-architecture library surfaces as
    // UnsatisfiedLinkError (an Error), and we must NOT rethrow from the static
    // initializer: doing so would poison this class with ExceptionInInitializerError
    // and break unrelated image features that merely share the package. Callers
    // check isNativeAvailable() and fall back when the native library is absent.
    private static volatile boolean nativeAvailable = false;

    static {
        // libimagequant.jnilib or libimagequant.so must be in java.library.path
//        System.loadLibrary("imagequant");
        try {
			NativeUtils.loadLibraryFromJar("/org/pngquant/libimagequant.jnilib");
			nativeAvailable = true;
		} catch (Throwable e) {
			try{
				NativeUtils.loadLibraryFromJar("/org/pngquant/libimagequant.so");
				nativeAvailable = true;
			}catch(Throwable err){
				nativeAvailable = false;
			}
		}
    }

    /**
     * @return true when the libimagequant native library is loaded and native
     *         quantization calls are safe to make on this platform.
     */
    public static boolean isNativeAvailable() {
        return nativeAvailable;
    }

    long handle;

    /**
     * Free memory used by the library. The object must not be used after this call.
     */
    abstract public void close();

    protected void finalize() throws Throwable {
        close();
    }
}
