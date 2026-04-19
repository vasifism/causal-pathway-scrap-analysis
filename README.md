
# Causal Pathway Analysis for Scrap Reduction

A compact showcase project that demonstrates how to move from  **causal reasoning → intervention decisions → actionable process changes** .

This repository is not about building a predictive model.
It is about answering the only question that matters in operations:

> **What should we change in the process to reduce scrap — and why?**

---

## 🚀 Core Idea

Most data projects stop at correlation:

* “X is associated with scrap”
* “Y has high importance”

This project goes one step further:

> **X influences scrap through a specific defect mechanism,
> and adjusting it in this direction reduces the KPI under these conditions.**

---

## 🧠 Methodology

The approach follows a structured causal workflow:

### 1. Causal Structure (DAG)

A predefined Directed Acyclic Graph is used to describe how:

* process variables
  → create defect mechanisms
  → which then drive scrap

---

### 2. Pathway-Based Decomposition

Instead of analyzing variables individually, the system is split into  **causal pathways** :

* Moisture
* Warpage
* Flash
* Stability

Each pathway represents a  **mechanism** , not just a correlation.

---

### 3. Actionable vs Non-Actionable Variables

Variables are explicitly separated into:

* **Controllable (intervenable)**
  → can be changed in production
* **Context / mechanism variables**
  → explain behavior but are not direct knobs

---

### 4. Intervention-Oriented Analysis

For each variable, the pipeline estimates:

* Direction of change (increase / decrease)
* Effect size (quartile-based gap)
* Strength of relationship
* Trade-offs (cycle time, energy)

The logic is intentionally simple and interpretable:

* compare low vs high operating regimes
* observe scrap response
* infer intervention direction

---

### 5. Recommendation Ranking

Final outputs are ranked based on:

* effect magnitude
* causal position (upstream > downstream)
* operational feasibility
* trade-off sensitivity

---

## 🔗 Main Causal Pathways

### Moisture Pathway (Most Actionable)

```
ambient_humidity_pct → dryer_dewpoint_c → resin_moisture_pct → splay → scrap_rate_pct
```

**Insight:**
The cleanest intervention is upstream — controlling dryer performance.

---

### Warpage Pathway (Largest Scrap Contribution)

```
mold_temperature_c + cooling_time_s → warpage → scrap_rate_pct
```

**Insight:**
High impact, but requires context-aware tuning.

---

### Flash Pathway

```
tool_wear_index + injection_pressure_bar + clamp_force_kn → flash → scrap_rate_pct
```

**Insight:**
Pressure control is effective, especially under tool wear conditions.

---

### Stability Pathway (Supporting)

```
maintenance → calibration_drift → instability → defects → scrap_rate_pct
```

**Insight:**
Important for system health and long-term performance, not a primary real-time knob.

---

## 📊 What the Code Produces

The pipeline generates:

* `defect_burden.csv` → where scrap is coming from
* `pathway_scores.csv` → how variables behave inside each pathway
* `intervention_ranking.csv` → ranked actionable levers
* `showcase_summary.md` → clean, presentation-ready summary

---

## 🧪 How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the showcase pipeline:

```bash
python -m src.datathon_showcase.run_showcase --csv data/synthetic_injection_molding_demo.csv
```

---

## 🎯 Key Contribution

This project demonstrates a shift from:

❌ correlation-based analysis
➡️
✅ causal, pathway-based intervention design

---

## ⚠️ Limitations

* This is  **DAG-guided reasoning** , not full causal identification
* Effects may vary by machine, product, or plant
* Results should be validated through controlled experiments

---

## 💡 One-Sentence Summary

> **This is not “what correlates with scrap”, but “which controllable levers inside known defect pathways should be changed to reduce it.”**

---

## 👤 Author

***Vasif Ismayilov,***

*Datathon 2026 Showcase
Causal Modeling & Process Optimization*
