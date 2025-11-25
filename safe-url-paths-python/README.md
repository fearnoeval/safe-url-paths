## safe-url-paths-python

- Calls runtime-agnmostic WASM written in Rust from Python via Wasmtime

```sh
# - Ensure you've built safe-url-paths-rust
#   - See the README.md in that directory for build instructions
ls -l ../safe-url-paths-rust/target/wasm32-unknown-unknown/release/safe_url_paths_rust.wasm

# - Run it
uv run main
```
