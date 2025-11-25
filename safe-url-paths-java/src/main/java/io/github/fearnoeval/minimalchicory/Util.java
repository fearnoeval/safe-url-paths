package io.github.fearnoeval.minimalchicory;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.stream.Collectors;

class Util {
    private static final int byteSize(final List<byte[]> bytess) {
        var size = 0;

        for (final var bytes : bytess) {
            size += bytes.length;
        }

        return size;
    }

    public record BytesAndSize(List<byte[]> bytes, int size) {}

    // public record BytesAndSizeAndSize(List<BytesAndSize> bytesAndSize, int size) {}

    public static final BytesAndSize toUtf8Bytes(List<String> ss) {
        final var bytes = ss.stream()
            .map(s -> s.getBytes(StandardCharsets.UTF_8))
            .collect(Collectors.toUnmodifiableList());

        final int size = byteSize(bytes);

        return new BytesAndSize(
            bytes,
            size
        );
    }
}
