package io.github.fearnoeval.minimalchicory.impl;

public record FatPointer32(ChicoryInstance chicoryInstance, int address, int size) implements AutoCloseable {
    @Override
    public void close() {
        this.chicoryInstance.deallocate(this);
    }
}
