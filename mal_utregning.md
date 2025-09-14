# Eksempel: Beregning av platevarmeveksler

Dette eksempelet viser steg-for-steg hvordan alle resultatverdier i `skript01.py` beregnes, med utgangspunkt i inputverdiene fra eksempelkoden. Dette kan brukes til validering og forståelse av beregningene.

## Inndata

```python
input_data = {
    "airstream_1": {
        "m_dot": 0.5,                # kg/s
        "temperature_c": 80.0,       # °C
        "phi": 0.3,                  # relativ fuktighet
        "pressure": 101325           # Pa
    },
    "airstream_2": {
        "m_dot": 0.6,                # kg/s
        "temperature_c": 20.0,       # °C
        "phi": 0.5,                  # relativ fuktighet
        "pressure": 101325           # Pa
    },
    "exchanger": {
        "width": 1.4,                # m
        "length": 1.4,               # m
        "plate_thickness": 0.0005,   # m
        "thermal_conductivity_plate": 15.0, # W/mK
        "number_of_plates": 30,
        "channel_height": 0.005      # m
    }
}
```

## 1. Geometri

- **Antall kanaler varm/kald:**
  - Varm: ceil((30+1)/2) = 16
  - Kald: floor((30+1)/2) = 15
- **Strømningstverrsnitt per kanal:**
  - width × channel_height = 1.4 × 0.005 = 0.007 m²
- **Totalt strømningstverrsnitt:**
  - Varm: 16 × 0.007 = 0.112 m²
  - Kald: 15 × 0.007 = 0.105 m²
- **Kanalhøyde:**
  - 0.005 m = 5 mm
- **Hydraulisk diameter:**
  - 2 × (1.4 × 0.005) / (1.4 + 0.005) ≈ 0.00998 m = 9.98 mm
- **Volum i veksler:**
  - Varm: 16 × 0.007 × 1.4 = 0.1568 m³
  - Kald: 15 × 0.007 × 1.4 = 0.147 m³
- **Total varmeoverflate:**
  - 30 × 2 × 1.4 × 1.4 = 117.6 m²

## 2. Luftparametre (beregnet for hver strøm)

For hver strøm:
- **Tetthet:**
  - ρ = p / (R × T)
  - R = 287.05 J/kgK
  - T (K) = temp + 273.15
- **Dynamisk viskositet:**
  - Sutherlands formel
- **Spesifikk varmekapasitet:**
  - cp = 1005 + 0.05 × (temp - 20)
- **Termisk konduktivitet:**
  - k = 0.024 + 0.00007 × temp
- **Prandtl-tall:**
  - Pr = 0.7 + 0.0002 × temp

**Eksempel for varm side:**
- T = 80 + 273.15 = 353.15 K
- ρ = 101325 / (287.05 × 353.15) ≈ 1.002 kg/m³
- cp = 1005 + 0.05 × (80-20) = 1005 + 3 = 1008 J/kgK
- k = 0.024 + 0.00007 × 80 = 0.024 + 0.0056 = 0.0296 W/mK
- Pr = 0.7 + 0.0002 × 80 = 0.716

## 3. Strømningsparametre

For hver side:
- **G (massestrømhastighet):** m_dot / A_flow
- **V (hastighet):** G / ρ
- **Q_vol (volumstrøm):** m_dot / ρ
- **Re (Reynolds):** ρ × V × D_h / μ
- **Strømningsregime:**
  - Laminær: Re < 2300
  - Overgang: 2300 ≤ Re ≤ 4000
  - Turbulent: Re > 4000

## 4. Varmeovergang og trykkfall

- **Nusselt-tall (Nu):**
  - Laminær: 3.66
  - Overgang/turbulent: se kode for formel
- **Varmeovergangstall (h):**
  - h = Nu × k / D_h
- **Trykkfall (Δp):**
  - Δp = f × (L/D_h) × (ρ × V²)/2
- **Friksjonsfaktor (f):**
  - Laminær: 64/Re
  - Overgang/turbulent: se kode

## 5. Motstander og U-verdi

- **Konvektiv motstand:**
  - r_conv = 1 / (h × A)
- **Konduktiv motstand plate:**
  - r_cond = plate_thickness / (λ × A)
- **Total motstand:**
  - r_total = r_conv_1 + r_cond + r_conv_2
- **U-verdi:**
  - U = 1 / (r_total × A)

## 6. Effektivitet og varmeoverføring

- **C_1, C_2:**
  - C = m_dot × cp
- **C_min, C_max:**
  - min/max av C_1, C_2
- **NTU:**
  - NTU = U × A / C_min
- **Effektivitet:**
  - effectiveness = 1 - exp((1/c_r) × NTU^0.22 × (exp(-c_r × NTU^0.78) - 1)), der c_r = C_min/C_max
- **Q_max:**
  - Q_max = C_min × (T1_in - T2_in)
- **Q_actual:**
  - Q_actual = effectiveness × Q_max

## 7. Resultater (fra kode)

- **Total U-verdi:**
- **Total varmeoverflate:**
- **NTU:**
- **C_min/C_max:**
- **Effektivitet:**
- **Maks varmeoverføring:**
- **Faktisk varmeoverføring:**

> Fyll inn alle tallverdier fra din kjøring for å validere!

---

Denne markdown-filen kan brukes som mal for manuell utregning og validering av alle steg i beregningen.
