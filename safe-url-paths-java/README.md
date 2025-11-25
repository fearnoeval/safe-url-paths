# `minimal-chicory`

## Commands

```sh
# - Ensure you've built safe-url-paths-rust
#   - See the README.md in that directory for build instructions
ls -l ../safe-url-paths-rust/target/wasm32-unknown-unknown/release/safe_url_paths_rust.wasm

# - Generate ./src/main/java/io/github/fearnoeval/minimalchicory/GeneratedWasmBlob.java
#   - gzip + Base64-encodes the WASM binary into a Java source file to avoid
#     reliance on filesystem paths at runtime
python3 wasm_to_java.py

# - target/ and create a JAR
mvn clean package

# - Run the JAR
java -jar target/safe-url-paths-java-0.0.1-SNAPSHOT.jar
```

## TODO

- Deallocation

## Resources

- [Chicory: Getting started](https://chicory.dev/docs/)
- [Using Memory to Share Data](https://chicory.dev/docs/usage/memory)
  - [Associated Rust code that compiled to WASM](https://github.com/dylibso/chicory/blob/f7f061d0413b968cabf4cfee5fd1752eaf6c8aff/wasm-corpus/src/main/resources/rust/count_vowels.rs)
