use std::mem;

use percent_encode::{percent_encode_no_slash, percent_encode_user_input};

mod percent_encode;

#[no_mangle]
pub extern "C" fn alloc(byte_size: i32) -> *const u8 {
    let mut buf = Vec::with_capacity(byte_size as usize);
    let ptr = buf.as_mut_ptr();
    mem::forget(buf);
    ptr
}

#[no_mangle]
pub unsafe extern "C" fn dealloc(ptr: &mut u8, len: i32) {
    let _ = Vec::from_raw_parts(ptr, 0, len as usize);
}

#[repr(C)]
pub struct WasmStrings {
    string_pointer: *const WasmString,
    size: i32,
}

impl WasmStrings {
    pub fn iter(&self) -> impl Iterator<Item = WasmString> {
        unsafe {
            let slices = std::slice::from_raw_parts(self.string_pointer, self.size as usize);
            slices.iter().copied()
        }
    }
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct WasmString {
    pub data: *const u8,
    pub size: usize,
}

impl WasmString {
    pub unsafe fn as_str(&self) -> Result<&str, std::str::Utf8Error> {
        let slice = std::slice::from_raw_parts(self.data, self.size);
        std::str::from_utf8(slice)
    }

    pub fn from_string(s: String) -> WasmString {
        let len = s.len();
        let data = s.as_ptr();

        std::mem::forget(s);

        WasmString {
            data,
            size: len,
        }
    }
}

#[no_mangle]
pub extern "C" fn interpolate(statics_ptr: *const WasmStrings, dynamics_ptr: *const WasmStrings) -> *const WasmString {
    let (statics, dynamics) = unsafe { 
        (
            &*statics_ptr,
            &*dynamics_ptr,
        )
    };

    let mut statics_iter = statics.iter();

    let mut ret = {
        let first = statics_iter.next().unwrap();
        let first_str = unsafe {
            first.as_str()
        }.unwrap();

        let mut ret = String::with_capacity(100);

        for &c in first_str.as_bytes() {
            ret.push_str(&percent_encode_no_slash(c));
        }

        ret
    };

    for (statik, dynamic) in statics_iter.zip(dynamics.iter()) {
        let (static_str, dynamic_str) = unsafe {
            (
                statik.as_str().unwrap(),
                dynamic.as_str().unwrap(),
            )
        };

        for &c in dynamic_str.as_bytes() {
            ret.push_str(&percent_encode_user_input(c));
        }

        for &c in static_str.as_bytes() {
            ret.push_str(&percent_encode_no_slash(c));
        }
    }

    let wasm_string = WasmString::from_string(ret);
    let wasm_string_boxed = Box::new(wasm_string);

    Box::into_raw(wasm_string_boxed)
}
