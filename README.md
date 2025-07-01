# Kor.ai – Surveillance Platform Core

Kor.ai is an AI-powered surveillance platform built to detect market abuse risks such as insider dealing and spoofing, with a focus on commodities and energy trading. This repository contains the core logic, Bayesian inference engine, data mapping, and service orchestration for alert generation.

---

## 🚀 Features

- Bayesian risk scoring using probabilistic models (via Agena API or `pgmpy`)
- Support for multiple abuse types: Insider Dealing, Spoofing
- Modular alert pipeline with raw → node transformation
- JSON-based model files and test case simulation
- Planned full open-source migration to pgmpy engine
- Cloud-ready for deployment in microservice or serverless form

---

## 📁 Repo Structure


---

## 🧪 How to Run (Local)

```bash
git clone https://github.com/ravkorsurv/kor-ai-core.git
cd kor-ai-core
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/app.py

---
