import sys
import weakref
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path

from wasmtime import Func, Instance, Memory, Module, Store


class AnsiEscapeSequence:
    RED = "\033[31m"
    RESET = "\033[0m"


def print_debug(msg: str) -> None:
    print(f"{AnsiEscapeSequence.RED}{msg}{AnsiEscapeSequence.RESET}", file=sys.stderr)


WASM_PATH = "../safe-url-paths-rust/target/wasm32-unknown-unknown/release/safe_url_paths_rust.wasm"

def get_wasm_path() -> Path:
    if (path := Path(WASM_PATH)) and not path.exists():
        print_debug(f"{repr(path)} does not exist; exiting")
        sys.exit(1)

    return path


with open (get_wasm_path(), "rb") as file:
    WASM_BYTES = file.read()


@dataclass(frozen=True)
class FatPointer32:
    instance: "WasmContext"
    address: int
    size: int


@dataclass(frozen=True)
class WasmContext:
    instance: Instance
    memory: Memory
    store: Store
    allocate_extern: Func
    deallocate_extern: Func
    interpolate_extern: Func

    def allocate(self, size: int) -> FatPointer32:
        return FatPointer32(
            instance=self,
            address=self.allocate_extern(self.store, size),
            size=size,
        )

    def deallocate(self, pointer: FatPointer32):
        if pointer is not None:
            self.deallocate_extern(self.store, pointer.address, pointer.size)


class PathInterpolator:
    @abstractmethod
    def interpolate(self, dynamics: list[str]) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class MemoryHelper:
    store: Store
    memory: Memory

    def read_i32(self, address: int) -> int:
        data_address = self.memory.read(self.store, address, address + Packer32.USIZE)

        return int.from_bytes(data_address, byteorder="little")

    def read_string(self, address: int) -> str:
        data_address = self.read_i32(address)
        data_size = self.read_i32(address + Packer32.USIZE)

        return self.memory.read(self.store, data_address, data_address + data_size).decode("utf-8")

    def write_i32(self, address: int, value: int):
        bytes = value.to_bytes(4, byteorder="little", signed=True)
        self.write_bytes(address, bytes)

    def write_bytes(self, address: int, value: bytes):
        self.memory.write(self.store, value, address)


class Packer32:
    USIZE = 4  # TODO: Python equivalent of Integer.BYTES?

    @staticmethod
    def pack_str(s: str) -> bytes:
        return s.encode(encoding="utf-8", errors="strict")

    @staticmethod
    def allocate_and_set(
        ctx: "WasmContext",
        ss: list[str],
    ) -> FatPointer32:
        # - Conversion
        string_count = len(ss)
        string_bytes = [Packer32.pack_str(s) for s in ss]
        string_bytes_size = sum(len(bs) for bs in string_bytes)

        # - Sizes
        array_pointer_and_size_size = Packer32.USIZE + Packer32.USIZE
        str_pointer_and_length_size = Packer32.USIZE + Packer32.USIZE
        all_length_and_pointer_size = string_count * str_pointer_and_length_size
        total_size = array_pointer_and_size_size + all_length_and_pointer_size + string_bytes_size

        try:
            ret = ctx.allocate(total_size)
            base_address = ret.address
            mem = MemoryHelper(store=ctx.store, memory=ctx.memory)

            string_pointer_base_offset = base_address + array_pointer_and_size_size
            string_data_offset = string_pointer_base_offset + all_length_and_pointer_size

            mem.write_i32(base_address, string_pointer_base_offset)
            mem.write_i32(base_address + Packer32.USIZE, string_count)

            for i in range(0, string_count):
                string_data = string_bytes[i]
                string_length = len(string_data)

                string_pointer_offset = string_pointer_base_offset + (i * str_pointer_and_length_size)
                string_length_offset = string_pointer_offset + Packer32.USIZE

                mem.write_i32(string_pointer_offset, string_data_offset)
                mem.write_i32(string_length_offset, string_length)
                mem.write_bytes(string_data_offset, string_data)

                string_data_offset += string_length

            return ret
        except Exception as e:
            raise e


@dataclass(frozen=True)
class PathInterpolatorWasmTime(PathInterpolator):
    statics_pointer: FatPointer32
    wasm_context: WasmContext = None  # type: ignore

    @staticmethod
    def _create(statics: list[str]) -> "PathInterpolatorWasmTime":
        if PathInterpolatorWasmTime.wasm_context is None:
            # - Create the WASM context
            store = Store()
            module = Module(store.engine, WASM_BYTES)
            instance = Instance(store, module, [])

            exports = instance.exports(store)

            memory = exports["memory"]

            # - Externed function names in the WASM
            allocate = exports["alloc"]
            deallocate =  exports["dealloc"]
            interpolate = exports["interpolate"]

            assert isinstance(memory, Memory)
            assert isinstance(allocate, Func)
            assert isinstance(deallocate, Func)
            assert isinstance(interpolate, Func)

            PathInterpolatorWasmTime.wasm_context = WasmContext(
                instance=instance,
                memory=memory,
                store=store,
                allocate_extern=allocate,
                deallocate_extern=deallocate,
                interpolate_extern=interpolate,
            )

        statics_pointer = Packer32.allocate_and_set(PathInterpolatorWasmTime.wasm_context, statics)

        return PathInterpolatorWasmTime(statics_pointer)

    def __post_init__(self):
        weakref.finalize(self, self._cleanup)

    def _cleanup(self):
        if self.statics_pointer:
            self.statics_pointer.instance.deallocate(self.statics_pointer)
            print_debug(f"Debug: Deallocated pointer at 0x{self.statics_pointer.address:0x}")

    def allocate(self, size: int) -> FatPointer32:
        ctx = PathInterpolatorWasmTime.wasm_context

        return FatPointer32(
            instance=ctx,
            address=ctx.allocate_extern(ctx.store, size),
            size=size,
        )

    def deallocate(self, pointer: FatPointer32):
        ctx = PathInterpolatorWasmTime.wasm_context

        if pointer is not None:
            ctx.deallocate_extern(ctx.store, pointer.address, pointer.size)

    def interpolate(self, dynamics: list[str]) -> str:
        ctx = PathInterpolatorWasmTime.wasm_context

        dynamics_pointer = Packer32.allocate_and_set(ctx, dynamics)
        fat_pointer_address: int = ctx.interpolate_extern(ctx.store, self.statics_pointer.address, dynamics_pointer.address)

        mem = MemoryHelper(ctx.store, ctx.memory)
        ret = mem.read_string(fat_pointer_address)

        self.deallocate(dynamics_pointer)

        return ret

    @staticmethod
    def default(statics: list[str]) -> PathInterpolator:
        return PathInterpolatorWasmTime._create(statics)


#

def perform_interpolation(statics: list[str], dynamics: list[str]):
    interpolator = PathInterpolatorWasmTime.default(statics)

    print(f"Interpolating {repr(dynamics)} into {statics}")

    result = interpolator.interpolate(dynamics)

    print(f"Result: {result}")


def main():
    statics_dynamics = [
        (
            ["/items/foo/", "/name"],
            ["42"],
        ),
        (
            ["/user/", "/items/", ""],
            ["123", "some/characters/../should be/escaped"],
        ),
    ]

    for statics, dynamics in statics_dynamics:
        perform_interpolation(statics, dynamics)
