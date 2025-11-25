package io.github.fearnoeval.minimalchicory.impl;

import java.util.List;

public interface IPathInterpolatorImpl {
    String interpolate(FatPointer32 instance, List<String> dynamics);
}
