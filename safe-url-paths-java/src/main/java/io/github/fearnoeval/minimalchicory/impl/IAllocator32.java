package io.github.fearnoeval.minimalchicory.impl;

public interface IAllocator32 {
    FatPointer32 allocate(int size);
    void deallocate(FatPointer32 pointer);
}
