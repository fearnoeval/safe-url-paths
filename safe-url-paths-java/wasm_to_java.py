import base64
import gzip
from typing import Generator


chars_per_line = 80 - len('        "" +')


def split_every_n(s: str, n: int) -> list[str]:
    return [s[i:i+n] for i in range(0, len(s), n)]

with open("../safe-url-paths-rust/target/wasm32-unknown-unknown/release/safe_url_paths_rust.wasm", "rb") as file:
    wasm_bytes = file.read()

wasm_bytes_gzipped = gzip.compress(wasm_bytes, 9)
wasm_bytes_gzipped_base64 = base64.b64encode(wasm_bytes_gzipped).decode("utf-8")
wasm_bytes_gzipped_base64_lines = split_every_n(wasm_bytes_gzipped_base64, chars_per_line)

print("WASM size                  ", len(wasm_bytes))
print("gzipped WASM size:         ", len(wasm_bytes_gzipped))
print("Base64'd gzipped WASM size:", len(wasm_bytes_gzipped_base64))

chars_per_line = 80 - len('        "" +')

encoded_lines = wasm_bytes_gzipped_base64_lines

# - Put together the output
out_lines = [
    "package io.github.fearnoeval.minimalchicory;",
    "",
    "import java.io.ByteArrayInputStream;",
    "import java.io.ByteArrayOutputStream;",
    "import java.io.IOException;",
    "import java.util.Base64;",
    "import java.util.zip.GZIPInputStream;",
    "",
    "class GeneratedWasmBlob {",
    "    private static final String WASM_BYTES_GZIPPED_BASE64 =",
]

# - Add all of the encoded lines
for encoded_line in encoded_lines:
    out_lines.append(f'        "{encoded_line}" +')

# - Finish up, adding:
#   - A finish to the string concatenation
#     - Cleaner output vs. cleaner code? In this case, former wins, IMO
#   - A closing curly brace for the class declaration and a newlines since it's
#     the end of the file

out_lines = out_lines + [
    '    "";',
    "",


    "    public static final byte[] WASM_BYTES = generateBytes();",
    "",
    "    private static final byte[] generateBytes() {",
    "        final var wasmBytesGzipped = Base64.getDecoder().decode(WASM_BYTES_GZIPPED_BASE64);",
    "        final var bais = new ByteArrayInputStream(wasmBytesGzipped);",
    "        final var wasmBytesBaos = new ByteArrayOutputStream();",
    "",
    "        try (var wasmBytesGzippedInputStream = new GZIPInputStream(bais)) {",
    "            final var buffer = new byte[4096];",
    "            int len;",
    "            while ((len = wasmBytesGzippedInputStream.read(buffer)) != -1) {",
    "                wasmBytesBaos.write(buffer, 0, len);",
    "            }",
    "        } catch (final IOException e) {",
    "            throw new RuntimeException(e);",
    "        }",
    "",
    "        return wasmBytesBaos.toByteArray();",
    "    }",
    "}\n",
]

with open("src/main/java/io/github/fearnoeval/minimalchicory/GeneratedWasmBlob.java", "w") as out_file:
    out_file.write("\n".join(out_lines))
