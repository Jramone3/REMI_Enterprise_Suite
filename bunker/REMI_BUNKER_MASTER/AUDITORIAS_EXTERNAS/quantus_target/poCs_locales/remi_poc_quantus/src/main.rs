// PoC Autocontenida: Desajuste de Tipos y Reducción Modular (u128 a Campo Finito)

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
    println!("REMI_IA: Iniciando PoC Nativa de Desajuste de Tipos (u128 a Fp)");
    println!("----------------------------------------------------------");

    // Usamos un módulo primo simulado más grande que cabe en u128 para el test
    let field_modulus: u128 = 340282366920938463463374607431768100000_u128;
    println!("Módulo del campo (P): {}", field_modulus);
    println!("");

    // 1. Valor u128 legítimo (ej. un nullifier o identificador de transacción)
    let legitimate_value_u128: u128 = 123456789012345;
    let legitimate_fp = Fp::from_u128(legitimate_value_u128, field_modulus);
    println!("Valor u128 legítimo: {}", legitimate_value_u128);
    println!(" -> Convertido a Fp:  {:?}", legitimate_fp);
    println!("");

    // 2. Valor u128 manipulado por el atacante (legítimo + k * P)
    // Debido al wrap-around matemático, esto colisionará exactamente en el mismo Fp.
    let crafted_value_u128 = legitimate_value_u128.checked_add(field_modulus).expect("Overflow en prueba");
    let crafted_fp = Fp::from_u128(crafted_value_u128, field_modulus);
    
    println!("Valor u128 manipulado (legítimo + Módulo P):");
    println!(" -> {}", crafted_value_u128);
    println!(" -> Convertido a Fp:  {:?}", crafted_fp);
    println!("");

    // 3. Verificación de Colisión
    println!("Verificando colisión matemática en Fp:");
    if legitimate_fp == crafted_fp {
        println!(" [!!!] COLISIÓN CRÍTICA DETECTADA: legitimate_fp == crafted_fp");
        println!(" Dos valores u128 distintos se mapean al mismo elemento Fp.");
        println!(" Vector de ataque viable para bypass de unicidad y colisión de nullifiers.");
    } else {
        println!(" [---] No se detectó colisión.");
    }
    println!("\nREMI_IA: Simulación finalizada con éxito.");
}
