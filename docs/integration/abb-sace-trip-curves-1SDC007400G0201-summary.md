# ABB SACE Low-Voltage Circuit Breakers — Trip Curves & Trip Units (Integration Reference)

> **Source:** ABB white paper *"Working with the Trip Characteristic Curves of ABB SACE
> Low Voltage Circuit-Breakers"*, document **`1SDC007400G0201`** (40 pages, EN).
> Summarized here for a future integration with these devices. This is a **summary**;
> the ABB white paper and the per-product technical catalogues / Modbus register maps
> are the authoritative sources.

## 0. What this document is (and is NOT)

This white paper explains how to **read and interpret the trip characteristic curves**
(trip curves, specific let-through energy curves, limitation curves) of ABB SACE
breakers built to the **US standards** UL 489, UL 1066, ANSI C37.13/16/17.

- ✅ It defines the **breaker families, trip units, protection functions and the
  adjustable parameters** (I1/t1, I2/t2, I3, I4/t4) that any integration must read or set.
- ❌ It is **not** a communications/protocol manual. It contains **no register maps**.
  The only connectivity hint: the Tmax **PR222DS/PD-A** trip unit adds a *dialogue unit*
  that integrates the breaker into a **Modbus RTU** network (p.22). For actual register
  maps, see the product catalogues and the Ekip/PR communication manuals (see §8).

---

## 1. Breaker families

| Family | Type | Models | Rated current (In) | Trip units | Notes |
|--------|------|--------|--------------------|------------|-------|
| **Tmax** | Molded-Case CB (MCCB) | T1 1P, T1, T2, T3, T4, T5, T6 | 15 A – 800 A | Thermomagnetic (TMF/TMD/TMA, MA) **or** electronic (PR221/PR222) | AC (UL 489). Some types (T2H, T4H/V, T5H/V) are **current-limiting**. Electronic units are AC-only. |
| **Emax** | LV Power CB (LVPCB) | E1, E2, E3, E4, E6 | 400 A – 5000 A | **Electronic only** (PR121/PR122/PR123) | AC (UL 1066), up to 635 V. Breaking up to 150 kA @ 240/480 V. |

Performance levels (interrupting rating) are coded by letter: Tmax `B/N/S/H/L/V`,
Emax `B-A/N-A/S-A/H-A/V-A/L-A`.

---

## 2. Trip unit types

### Thermomagnetic (Tmax only)
- **Thermal part** (bimetal) → overload protection **L**, inverse-time delay.
- **Magnetic part** (electromagnet) → instantaneous short-circuit protection **I**,
  trips in tens of ms.
- Variants: **TMF** (fixed thermal + fixed magnetic), **TMD** (adjustable thermal, fixed
  magnetic), **TMA** (adjustable thermal + adjustable magnetic), **MA/MF** (magnetic-only).

### Electronic (Tmax: PR221/PR222; Emax: PR121/PR122/PR123)
Microprocessor-based; more precise thresholds and times. Implement up to four protection
functions (see §3). The higher models add ground-fault, measurement, communications.

| Trip unit | Fits | Functions | Comms |
|-----------|------|-----------|-------|
| PR221DS-I | Tmax T2/T4/T5/T6 | I only (motor protection) | — |
| PR221DS-LS/I | Tmax T2/T4/T5/T6 | L-S-I | — |
| PR222DS/P | Tmax T4/T5/T6 | L-S-I-G | — |
| **PR222DS/PD-A** | Tmax T4/T5/T6 | L-S-I-G | **Modbus RTU** (dialogue unit) |
| PR121/P | Emax E1–E6 | L-S-I (G optional) | — |
| PR122/P | Emax E1–E6 | L-S-I-G + measurement | comms/signalling module |
| PR123/P | Emax E1–E6 | L-S-I-G (richest) | comms/signalling module |

---

## 3. Protection functions and their parameters

These are the **core adjustable values** an integration reads/writes. ANSI relay codes in
parentheses.

| Func | Name (ANSI) | Pickup (current) | Delay (time) | Curve | Can disable? |
|------|-------------|------------------|--------------|-------|--------------|
| **L** | Overload / long-time (51) | **I1** = long-time pickup | **t1** = long-time delay | inverse, I²t = K | **No** (always on) |
| **S** | Short-circuit, delayed / short-time (51) | **I2** = short-time pickup | **t2** = short-time delay | I²t = K **or** t = K (selectable) | Yes |
| **I** | Instantaneous short-circuit (50) | **I3** = instantaneous pickup | none (instantaneous) | — | Yes (override remains) |
| **G** | Ground fault (51N) | **I4** = ground-fault pickup | **t4** = ground-fault delay | I²t = K **or** t = K | Yes |

Key reference multiples (where the delay time is specified):
- **L** delay t1 is referenced at **3×I1** (Emax) / **6×I1** (Tmax).
- **S** delay t2 is referenced at **10×In** (Emax) / **8×In** (Tmax).

### Typical setting ranges (×In, electronic units)

| Param | Tmax PR221DS-LS/I | Tmax PR222DS/P | Emax PR121/122/123 |
|-------|-------------------|-----------------|---------------------|
| **I1** (L) | 0.4–1 ×In, I²t=K | 0.4–1 ×In, I²t=K | 0.4–1 ×In, t=K/I² |
| **I2** (S) | 1–10 ×In, I²t=K | 0.6–10 ×In (I²t ON/OFF) | 0.6–10 ×In (t=K/I² or t=K) |
| **I3** (I) | 1–10 ×In | 1–10 ×In | 1.5–15 ×In |
| **I4** (G) | — | present (G) | 0.2–1 ×In (t=K/I² or t=K) |
| **t2** (S) example | — | 0.05 / 0.1 / 0.25 / 0.5 s | settable |
| **t4** (G) example | — | 0.1 / 0.2 / 0.4 / 0.8 s | settable |

> Thermomagnetic TMA (example): thermal **I1 = (0.7–1)×In**, magnetic **I3 = (5–10)×In**;
> magnetic-only **MA: I3 = (6–12)×In**.

---

## 4. How a setting is computed (worked examples from the paper)

**Overload (L):** `Setting_L = Ib / In`, then pick the **next available value ≥** result.
- Example: T5N400, In=400 A, load Ib=340 A → 340/400 = 0.85 → **I1 = 0.85×400 = 340 A**.

**Instantaneous (I):** `Setting_I = Ik_min / In`, then pick the **next available value ≤**
result (so that **I3 ≤ Ik_min**).
- Example: In=400 A, Ik_min=3000 A → 3000/400 = 7.5 → **I3 = 7.5×400 = 3000 A**.

**Electronic dip-switch example (PR222DS/P, In=150 A):**
- L: `Setting = 69/150 = 0.46`; I1 = In×(0.4 + 0.02 + 0.04) = **69 A** (the 0.4 base is
  always added).
- I: `Setting = 1500/150 = 10`; pick 9.5 → I3 = In×(1.5+3+5) = **1425 A** (≤ Ik_min).

> Integration takeaway: the device stores **multiplier coefficients** (×In), not raw amps.
> Convert to amps using **In** of the installed rating plug. The base **0.4** for L is added
> by default.

---

## 5. Trip-curve shape (for monitoring/coordination logic)

- Plotted on **bilogarithmic axes**: current `I` (×In or kA) vs trip time `t` (s).
- **L** is a negative-slope inverse-time line (I²t = K) — a "pencil" of parallel curves
  selected by t1.
- **S** is either inverse (I²t = K) or a horizontal constant-time segment (t = K).
- **I** is a vertical line at I3 (instantaneous).
- **G** mirrors S (I²t = K or t = K).
- **Current-limiting** breakers cut the let-through **I²t** and **peak current** below the
  prospective half-cycle values (Ch.6) — relevant for energy/let-through calculations.

---

## 6. Emax trip times (device-level latencies, useful for control expectations)

- **Make time (max):** ~80 ms.
- **Break time:** ~70 ms for currents below short-time pickup; ~30 ms (down to ~12 ms on
  E2 H-A) above it.

---

## 7. Tolerances & key definitions (Annex A / glossary)

- Real trip points have **tolerance bands** around the nominal curve — integration logic
  must treat thresholds as ranges, not exact points.
- Important terms: **In** (rated current / rating plug), **Ir/I1** (current setting),
  **Ik_min** (min prospective short-circuit current), **I²t** (let-through energy, A²s),
  **prospective vs limited current**, **instantaneous override** (fixed level that trips
  regardless of settings).

---

## 8. Integration notes & next steps

**What this device exposes for software integration**
- The trip unit holds **configuration** (I1/t1, I2/t2 + I²t on/off, I3, I4/t4, curve type,
  function enable/disable) and, on higher models (PR122/PR123, and Ekip on newer ranges),
  **measurements** (currents, voltages, power, energy) and **status/alarms**.
- **Communications:** classic PR units use **Modbus RTU** via a dialogue/PR-COM module
  (e.g. Tmax **PR222DS/PD-A**). Newer ABB ranges use **Ekip** trip units + **Ekip Com**
  modules (Modbus RTU/TCP, Profibus, Profinet, EtherNet/IP, IEC 61850).

**To actually build the integration we still need (not in this document):**
1. The **Modbus register map** for the specific trip unit / Com module (addresses, scaling,
   read/write access, function codes).
2. The exact **device + trip unit + Com module** model on site (this drives both the
   parameter ranges above and the register map).
3. Whether the integration is **read-only** (monitor measurements/status/settings) or also
   **write/control** (change protection settings, open/close) — the latter has safety and
   access-control implications.

**Suggested approach for this repo**
- Read-only monitoring over **Modbus TCP** (via an RTU↔TCP gateway if the unit is RTU) is
  the lowest-risk first step.
- A small adapter service can poll Modbus registers and expose them as JSON, mirroring the
  pattern of the existing Python API (`src/api`). Convert ×In coefficients → amps using the
  device **In**.

**Reference documents to obtain from ABB next**
- "ABB Molded Case Circuit Breakers UL 489 and CSA C22.2" catalogue (Tmax / PR221/PR222).
- "Emax Low Voltage Power Circuit Breakers" catalogue (PR121/PR122/PR123).
- The trip unit's **Modbus communication manual / register map** (the actual integration
  contract).

---

### Document map (white paper chapters)
1. Introduction · 2. Definitions · 3. Tmax & Emax families ·
4. Trip units (thermomagnetic + electronic, functions L/S/I/G) ·
5. Trip curves · 6. Current-limiting let-through (I²t, peak) ·
Annex A: tolerances · Glossary.
