const SOLIDUS_BYTE: u8 = '/' as u8;
const SOLIDUS_STR: &str = "/";

const PERCENT_ENCODE: [&str; 256] = [
    "%00", "%01", "%02", "%03", "%04", "%05", "%06", "%07", "%08", "%09", "%0A", "%0B", "%0C", "%0D", "%0E", "%0F",
    "%10", "%11", "%12", "%13", "%14", "%15", "%16", "%17", "%18", "%19", "%1A", "%1B", "%1C", "%1D", "%1E", "%1F",
    "%20", "%21", "%22", "%23", "%24", "%25", "%26", "%27", "%28", "%29", "%2A", "%2B", "%2C", "-",   ".",   "%2F",
    "0",   "1",   "2",   "3",   "4",   "5",   "6",   "7",   "8",   "9",   "%3A", "%3B", "%3C", "%3D", "%3E", "%3F",
    "%40", "A",   "B",   "C",   "D",   "E",   "F",   "G",   "H",   "I",   "J",   "K",   "L",   "M",   "N",   "O",
    "P",   "Q",   "R",   "S",   "T",   "U",   "V",   "W",   "X",   "Y",   "Z",   "%5B", "%5C", "%5D", "%5E", "_",
    "%60", "a",   "b",   "c",   "d",   "e",   "f",   "g",   "h",   "i",   "j",   "k",   "l",   "m",   "n",   "o",
    "p",   "q",   "r",   "s",   "t",   "u",   "v",   "w",   "x",   "y",   "z",   "%7B", "%7C", "%7D", "~",   "%7F",
    "%80", "%81", "%82", "%83", "%84", "%85", "%86", "%87", "%88", "%89", "%8A", "%8B", "%8C", "%8D", "%8E", "%8F",
    "%90", "%91", "%92", "%93", "%94", "%95", "%96", "%97", "%98", "%99", "%9A", "%9B", "%9C", "%9D", "%9E", "%9F",
    "%A0", "%A1", "%A2", "%A3", "%A4", "%A5", "%A6", "%A7", "%A8", "%A9", "%AA", "%AB", "%AC", "%AD", "%AE", "%AF",
    "%B0", "%B1", "%B2", "%B3", "%B4", "%B5", "%B6", "%B7", "%B8", "%B9", "%BA", "%BB", "%BC", "%BD", "%BE", "%BF",
    "%C0", "%C1", "%C2", "%C3", "%C4", "%C5", "%C6", "%C7", "%C8", "%C9", "%CA", "%CB", "%CC", "%CD", "%CE", "%CF",
    "%D0", "%D1", "%D2", "%D3", "%D4", "%D5", "%D6", "%D7", "%D8", "%D9", "%DA", "%DB", "%DC", "%DD", "%DE", "%DF",
    "%E0", "%E1", "%E2", "%E3", "%E4", "%E5", "%E6", "%E7", "%E8", "%E9", "%EA", "%EB", "%EC", "%ED", "%EE", "%EF",
    "%F0", "%F1", "%F2", "%F3", "%F4", "%F5", "%F6", "%F7", "%F8", "%F9", "%FA", "%FB", "%FC", "%FD", "%FE", "%FF",
];

pub(crate) fn percent_encode_no_slash(c: u8) -> &'static str {
    if c == SOLIDUS_BYTE {
        SOLIDUS_STR
    } else {
        PERCENT_ENCODE[c as usize]
    }
}

pub(crate) fn percent_encode_user_input(c: u8) -> &'static str {
    PERCENT_ENCODE[c as usize]
}

#[cfg(test)]
mod test {
    /// [RFC 3986: 2.3. Unreserved Characters](https://www.rfc-editor.org/rfc/rfc3986#section-2.3)
    const fn is_unreserved(b: u8) -> bool {
        match b {
            b'A'..=b'Z'
            | b'a'..=b'z'
            | b'0'..=b'9'
            | b'-' | b'.' | b'_' | b'~' => true,
            _ => false,
        }
    }

    #[test]
    fn test_all_percent_encoded_values_user_input() {
        for c in u8::MIN..=u8::MAX {
            let expected = if is_unreserved(c) {
                (c as char).to_string()
            } else {
                format!("%{:02X}", c)
            };

            let actual = super::percent_encode_user_input(c);

            assert_eq!(actual, expected)
        }
    }

    #[test]
    fn test_all_percent_encoded_values_no_slash() {
        for c in u8::MIN..=u8::MAX {
            let expected = if is_unreserved(c) {
                (c as char).to_string()
            } else if c == super::SOLIDUS_BYTE {
                super::SOLIDUS_STR.to_string()
            } else {
                format!("%{:02X}", c)
            };

            let actual = super::percent_encode_no_slash(c);

            assert_eq!(actual, expected)
        }
    }
}
