# safe-url-paths-rust

## Building

```sh
# - One-time setup
rustup target add wasm32-unknown-unknown

# - Running the tests
#   - Adjust the target triple as necessary since the build target is set to
#     wasm32-unknown-unknown in .cargo/config.toml
cargo test --target x86_64-unknown-linux-gnu

# - Building
cargo build --release
```

## Note

- As written, this follows the spec closely and does not escape apostrophe,
  though it probably should as a precaution
