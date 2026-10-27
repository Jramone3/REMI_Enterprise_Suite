use anyhow::Result;

fn main() -> Result<()> {
    println!("🛡️ INICIANDO SIMULACIÓN DE POC: Test de Nullifier Duplicado en Lote Privado");

    let n_leaf: usize = 16;
    let scale_down_factor: u128 = 10_000_000_000; // 10^10 escalado on-chain

    let mut simulated_nullifiers: Vec<String> = Vec::with_capacity(n_leaf);

    let nullifier_malicioso = "0xDEADBEEFCAFE0000";
    simulated_nullifiers.push(nullifier_malicioso.to_string());
    simulated_nullifiers.push(nullifier_malicioso.to_string()); // Duplicado intencional

    for i in 2..n_leaf {
        simulated_nullifiers.push(format!("0xUNIQUE_NULLIFIER_{}", i));
    }

    println!("🔍 Analizando unicidad de nullifiers en el lote de {} slots...", n_leaf);

    let mut unique_check = std::collections::HashSet::new();
    let mut colision_detectada = false;

    for n in &simulated_nullifiers {
        if !unique_check.insert(n) {
            println!("🚨 ANOMALÍA DETECTADA: Nullifier duplicado encontrado en el slot: {}", n);
            colision_detectada = true;
        }
    }

    if colision_detectada {
        println!("⚠️ Resultado de la PoC: El circuito fallaría si no restringe 'pairwise_distinct' estrictamente a nivel de restricciones Plonky2.");
    } else {
        println!("✅ El circuito bloqueó correctamente la colisión.");
    }

    let monto_manipulado_circuit: u128 = u128::MAX / 2; 
    let resultado_overflow = monto_manipulado_circuit.checked_mul(scale_down_factor);

    match resultado_overflow {
        Some(val) => println!("⚖️ Cálculo de escala seguro: {}", val),
        None => println!("💥 VULNERABILIDAD POTENCIAL: Overflow detectado en el factor de escala de 10^10. Riesgo de mint inflado on-chain."),
    }

    Ok(())
}
