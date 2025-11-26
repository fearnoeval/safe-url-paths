# safe-url-paths

A proof-of-concept URL path interpolation library written in Rust compiled to vanilla WebAssembly (`wasm32-unknown-unknown`) with no bindings to a specific operating system, architecture, or host language runtime

Note that this library alone is not sufficient for handling arbitrary user input, but may be used in conjunction with other checks, restrictions, etc.

```rust
// - Example host usage
//   - Dynamic (interpolated) portions are percent-encoded in accordance with
//     RFC 3986
//   - Static portions are percent-encoded in accordance with RFC 3986 except
//     for the slash (solidus)

url_path!("/user/{user_id}/product/{product_id}")`;
//         \____/\_______/\_______/\__________/
//          \     \        \        \
//           \     \        \        - fully encoded
//            \     \        - fully encoded except for slashes
//             \     - fully encoded
//              - fully encoded except for slashes
```

## Note

- The emphasis of this project is on the agnostic library concept
  - URL path interpolation was simply top-of-mind because I was thinking about SSRF prevention at the same time
- Not production ready
- Despite list usage, this is not LLM-generated; I've been writing in this style [since](https://github.com/fearnoeval/game-of-life/commit/32b466b86d8097a8ff534d275a5e48a9a7bc674d) [before](https://github.com/fearnoeval/tetrish/commit/98697f68a68b7cb166ddf73ccd2fceb57f1d9a3a) [it](https://github.com/fearnoeval/image-slideshow/commit/ed3b825320ebb4c066538182a074a4936024f9ae) [was](https://github.com/fearnoeval/yenc-encoder/commit/4974a0a9165fcd6eb670d5ab223d87f0d064e677) [popularized](https://github.com/fearnoeval/nntp-client/commit/f99c9c14394af7bb226f77c40b5fa83e9192eee0)

## Why?

- Libraries generally can't be shared across different architectures, operating systems, and/or language runtimes, leading to an explosion of implementations, even for things that have well-defined specifications
- WASM runtimes are available for a wide variety of languages
- [Writing your own WASM runtime can mostly be done within a conference talk](https://youtu.be/r-A78RgMhZU)
- This aims to prove that one can have a single implementation of a library that works across the boundaries mentioned above

## What's here?

- Proof-of-concept of:
  - [`safe-url-paths-rust/`](safe-url-paths-rust/): A URL path interpolation library written in Rust that targets WASM in a runtime-agnostic manner
  - [`safe-url-paths-java/`](safe-url-paths-java/): A Java application using the [Chicory](https://github.com/dylibso/chicory) WASM runtime to consume the library
  - [`safe-url-paths-python/`](safe-url-paths-python/): A Python application using the [Wasmtime](https://github.com/bytecodealliance/wasmtime-py) WASM runtime to consume the library

## Downsides?

- The path interpolation is written in a specific style where there are both static and dynamic components
  - The main difference between the two is that slashes are not percent-encoded in static portions; for example:
  - The target use case is contexts where custom interpolation handlers are supported
    - Scala's [custom interpolators](https://docs.scala-lang.org/scala3/book/string-interpolation.html#custom-interpolators)
    - Rust via a macro similar to [`format!`](https://doc.rust-lang.org/std/macro.format.html)
    - JavaScript's [tagged template literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#tagged_templates)
- Performance is worse than using the host language directly
- Each host must implement packing/unpacking for data that crosses the WASM boundary and back
- The implementation is good enough for the examples, but could use more serious thought
- More complicated libraries may be harder or impossible to implement with this approach
  - It's [not a silver bullet](https://en.wikipedia.org/wiki/No_Silver_Bullet), but the concept may resemble a shiny, gray projectile for some use cases

## Production-ready?

- Absolutely not

## Resources

- [RFC 3986: Uniform Resource Identifier (URI): Generic Syntax](https://www.rfc-editor.org/rfc/rfc3986)
- [WebAssembly Specification — WebAssembly 3.0 (2025-11-22)](https://webassembly.github.io/spec/core/)
- [Wasmtime: A fast and secure runtime for WebAssembly](https://wasmtime.dev/)
- [Chicory: A JVM native WebAssembly runtime](https://chicory.dev/)
- [Server-side request forgery - Wikipedia](https://en.wikipedia.org/wiki/Server-side_request_forgery)
- [A Talk Near the Future of Python (a.k.a., Dave live-codes a WebAssembly Interpreter) - YouTube](https://www.youtube.com/watch?v=r-A78RgMhZU)

## Historical notes

- Initially implemented in November 2024
- Cleaned up and opened up in November 2025

## License

- © 2024-2025 [Tim Walter](https://www.fearnoeval.com/)
- [Mozilla Public License 2.0](LICENSE)
