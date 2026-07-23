# 📄 Documentación Técnica — Hardware Activo: jramonrivasg  
**Fecha:** lunes 27 de octubre de 2025  
**Hora:** 18:56 (VET)  
**Autor:** jramonrivasg  
**Ubicación:** Turmero, Estado Aragua, Venezuela

> **Nota:** El sistema REMI es un producto derivado de la expansión del toolkit **MintBridge v1.0**, creado como núcleo patrimonial modular y trazable.

---

## 🖥️ Placa Base y Procesador

| Componente     | Detalles                                 |
|----------------|------------------------------------------|
| Placa base     | Intel DP55WB                             |
| CPU            | Intel Core i5-650 @ 3.20 GHz (2 núcleos / 4 hilos) |
| Arquitectura   | x86_64                                   |
| RAM instalada  | 8 GB DDR3                                |
| Expansión RAM  | Planificada (slots disponibles)          |

---

## 💾 Almacenamiento

| Partición   | Montaje             | Capacidad | Uso actual | Estado técnico |
|-------------|---------------------|-----------|------------|----------------|
| `/dev/sda5` | `/` (raíz)          | 134 GB    | 45 GB (35%)| Limpio, sin residuos patrimoniales |
| `/dev/sda7` | `/mnt/REMI_datos`   | 96 GB     | 11 GB (13%)| Núcleo patrimonial consolidado     |

---

## 🎮 Gráficos

| Componente     | Detalles                                 |
|----------------|------------------------------------------|
| GPU            | NVIDIA GeForce 8600 GT                   |
| Estado         | Operativa con refrigeración externa      |
| Driver         | Legacy NVIDIA compatible con Xorg       |

---

## 📡 Red y Conectividad

| Tipo       | Modelo / Chipset         | Estado     | Driver       |
|------------|--------------------------|------------|--------------|
| Ethernet   | Intel 82578DC Gigabit    | Inactivo   | `e1000e`     |
| Wi-Fi PCIe | Realtek RTL8192EE        | ✅ Activo  | `rtl8192ee`  |
| Bluetooth  | Cambridge CSR USB Dongle | ✅ Activo  | `btusb`      |
| USB Wi-Fi  | Realtek RTL8188EU        | ❌ Retirado (dañado) |

---

## 🔌 Periféricos USB

| Dispositivo        | Modelo / ID         |
|--------------------|---------------------|
| Teclado            | CASUE USB KB (2a7a:959f) |
| Mouse              | Sigma Micro (1c4f:0048) |
| Bluetooth Dongle   | Cambridge CSR (0a12:0001) |

---

## ✅ Estado General del Sistema

- **Sistema operativo:** Linux Mint XFCE
- **Kernel:** 5.15.0-160-generic
- **Conectividad:** Wi-Fi y Bluetooth activos
- **Depuración:** Eliminados residuos de hardware obsoleto
- **Auditoría:** Scripts activos (`estado_REMI.sh`, `revisar_REMI_datos.sh`)
- **Expansión:** RAM y almacenamiento listos para ampliación

---

