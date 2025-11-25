package io.github.fearnoeval.minimalchicory.impl;

import java.nio.charset.StandardCharsets;
import java.util.List;

import com.dylibso.chicory.runtime.ExportFunction;
import com.dylibso.chicory.runtime.Instance;
import com.dylibso.chicory.runtime.Memory;

public class ChicoryInstance implements IAllocator32, IPathInterpolatorImpl {
    public final Instance instance;
    public final Memory memory;
    private final ExportFunction allocate;
    private final ExportFunction deallocate;
    private final ExportFunction interpolate;

    public ChicoryInstance(Instance instance) {
        this.instance = instance;
        this.memory = instance.memory();
        // - Externed function names
        this.allocate = instance.export("alloc");
        this.deallocate = instance.export("dealloc");
        this.interpolate = instance.export("interpolate");
    }

    @Override
    public FatPointer32 allocate(int size) {
        return new FatPointer32(this, (int) this.allocate.apply(size)[0], size);
    }

    @Override
    public void deallocate(final FatPointer32 pointer) {
        if (pointer != null) {
            this.deallocate.apply(pointer.address(), pointer.size());
        }
    }

    @Override
    public String interpolate(final FatPointer32 instance, final List<String> dynamics) {
        try (var dynamicsPacked = Packer32.allocateAndSet(this, dynamics)) {
            System.out.println("Address: " + dynamicsPacked.address());
            final var rets = this.interpolate.apply(
                instance.address(),
                dynamicsPacked.address()
            );
            final var fatPointerAddress = (int) rets[0];

            final var dataAddress = (int) this.memory.readI32(fatPointerAddress);
            final var dataSize = (int) this.memory.readI32(fatPointerAddress + Packer32.USIZE);

            return this.memory.readString(dataAddress, dataSize, StandardCharsets.UTF_8);
        }
    }
}
