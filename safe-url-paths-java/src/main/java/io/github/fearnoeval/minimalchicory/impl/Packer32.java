package io.github.fearnoeval.minimalchicory.impl;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.stream.Collectors;

public class Packer32 {
    private Packer32() {}

    public static final int USIZE = Integer.BYTES;

    public static final byte[] pack(final String s) {
        return s.getBytes(StandardCharsets.UTF_8);
    }

    public static final FatPointer32 allocateAndSet(
        final ChicoryInstance instance,
        final List<String> ss
    ) {
        // - Conversion
        final var stringCount = ss.size();
        final var stringBytes = ss.stream().map(Packer32::pack).collect(Collectors.toList());
        final var stringBytesSize = stringBytes.stream().mapToInt(bs -> bs.length).sum();

        // - Sizes
        final var arrayPointerAndSizeSize = Packer32.USIZE + Packer32.USIZE;
        final var strPointerAndlengthSize = Packer32.USIZE + Packer32.USIZE;
        final var allLengthAndPointerSize = stringCount * strPointerAndlengthSize;
        final int totalSize = arrayPointerAndSizeSize + allLengthAndPointerSize + stringBytesSize;

        FatPointer32 ret = null;

        try {
            // - Allocation
            ret = instance.allocate(totalSize);
            final var baseAddress = ret.address();
            final var mem = instance.memory;

            // - Fixed offset
            final var stringPointerBaseOffset = baseAddress + arrayPointerAndSizeSize;
            // - Variable offset; modified in the loop
            var stringDataOffset = stringPointerBaseOffset + allLengthAndPointerSize;

            // - Write array pointer and size
            mem.writeI32(baseAddress, stringPointerBaseOffset);
            mem.writeI32(baseAddress + Packer32.USIZE, stringCount);

            // - Write string pointers, sizes, and data
            for (var i = 0; i < stringCount; ++i) {
                final var stringData = stringBytes.get(i);
                final var stringLength = stringData.length;

                final var stringPointerOffset = stringPointerBaseOffset + (i * strPointerAndlengthSize);
                final var stringLengthOffset = stringPointerOffset + Packer32.USIZE;

                mem.writeI32(stringPointerOffset, stringDataOffset);
                mem.writeI32(stringLengthOffset, stringLength);
                mem.write(stringDataOffset, stringData);

                // - Update string data offset
                stringDataOffset += stringLength;
            }

            return ret;
        } catch (final Throwable t) {
            if (ret != null) {
                instance.deallocate(ret);
            }
            throw t;
        }
    }
}
