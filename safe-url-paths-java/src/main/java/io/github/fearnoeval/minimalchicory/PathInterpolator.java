package io.github.fearnoeval.minimalchicory;

import java.util.List;

import com.dylibso.chicory.runtime.Store;
import com.dylibso.chicory.wasm.Parser;

import io.github.fearnoeval.minimalchicory.impl.IPathInterpolator;
import io.github.fearnoeval.minimalchicory.impl.Packer32;
import io.github.fearnoeval.minimalchicory.impl.ChicoryInstance;

public class PathInterpolator {
    private PathInterpolator() {}

    public static final IPathInterpolator defaultImplementation(final List<String> statics) {
        final ChicoryInstance chicoryInstance;
        {
            final var module = Parser.parse(GeneratedWasmBlob.WASM_BYTES);
            final var wasmInstance = new Store().instantiate("safe-url-paths-rust", module);
            chicoryInstance = new ChicoryInstance(wasmInstance);
        };

        final var staticsPointer = Packer32.allocateAndSet(chicoryInstance, statics);

        return new IPathInterpolator() {
            @Override
            public String interpolate(List<String> dynamics) {
                return chicoryInstance.interpolate(staticsPointer, dynamics);
            }
        };
    }
}
