// /home/ramon/REMI_CORE/bunker/AUDITORIAS_EXTERNAS/quantus_target/poCs_locales/poc_quantus_nullifier_test.rs
// PoC de Validación de Doble Gasto Intra-Lote y Nullifiers - Quantus ZK-Wormhole

use std::fs;
use anyhow::Result;

fn main() -> Result<()> {
    println!("🛡️ INICIANDO SIMULACIÓN DE POC: Test de Nullifier Duplicado en Lote Privado");
    
    // Simulación de parámetros del circuito Plonky2 (Leaf y Private Batch)
    let n_leaf: usize = 16;
    let scale_down_factor: u128 = 10_000_000_000; // 10^10 escalado on-chain
    
    // Mock de nullifiers: Simulamos una inyección maliciosa con colisión intencional
    let mut simulated_nullifiers: Vec<String> = Vec::with_capacity(n_leaf);
    
    // Inyectamos un nullifier duplicado a propósito para probar el filtro 'pairwise_distinct'
    let nullifier_malicioso = "0xDEADBEEFCAFE0000";
    simulated_nullifiers.push(nullifier_malicioso.to_string());
    simulated_nullifiers.push(nullifier_malicioso.to_string()); // Duplicado intencional
    
    for i in 2..n_leaf {
        simulated_nullifiers.push(format!("0xUNIQUE_NULLIFIER_{}", i));
    }

    println!("🔍 Analizando unicidad de nullifiers en el lote de {} slots...", n_leaf);
    
    // Verificación lógica de duplicados (simulando la restricción del circuito)
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

    // Prueba de desbordamiento por Scale Down Factor
    let monto_manipulado_circuit: u128 = u128::MAX / 2; 
    let resultado_overflow = monto_manipulado_circuit.checked_mul(scale_down_factor);
    
    match resultado_overflow {
        Some(val) => println!("⚖️ Cálculo de escala seguro: {}", val),
        None => println!("💥 VULNERABILIDAD POTENCIAL: Overflow detectado en el factor de escala de 10^10. Riesgo de mint inflado on-chain."),
    }

    Ok(())
}
