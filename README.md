<div align="center">

# Samarjith Biswas, Ph.D.

**I make physics simulation fast enough to design with.**

Research Scientist III · NewFoS Center, University of Arizona
Mechanical & Aerospace Engineering Ph.D. · Acoustics, wave physics, and machine learning

[![Website](https://img.shields.io/badge/samarjithbiswas.com-005F73?style=flat&logo=googlechrome&logoColor=white)](https://samarjithbiswas.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/samarjithbiswas/)
[![Google Scholar](https://img.shields.io/badge/Google_Scholar-4285F4?style=flat&logo=googlescholar&logoColor=white)](https://scholar.google.com/citations?user=EyxF_uoAAAAJ)
[![Email](https://img.shields.io/badge/Email-D14836?style=flat&logo=gmail&logoColor=white)](mailto:samarjithbiswas@arizona.edu)

</div>

---

A finite-element solve of a phononic crystal takes one to three hours. I built
[**PhononIQ**](https://samarjithbiswas.github.io/phononiq/), a physics-informed
deep-learning surrogate that gives the same answer in about **5 milliseconds**
at R² ≈ 0.98, and runs in your browser. Getting there meant owning every layer:
generating training data from thousands of automated simulations, designing the
network architectures, engineering physics-informed losses that cut unphysical
predictions by 57%, and validating against ground truth before believing any of it.

The same discipline runs through my research: model it, build it, measure it,
and make the model and the measurement agree, currently to within **±2%**.

**Proof points**

- Lead author, *Scientific Reports* (2026): directional interface modes in topological acoustic metamaterials, with A. Alù (CUNY/ASRC) and M. Leamy (Georgia Tech) · [DOI 10.1038/s41598-026-62783-x](https://doi.org/10.1038/s41598-026-62783-x)
- Co-author, *Physical Review Applied* **25**, 054035 (2026): composite superlattice SAW RF devices
- US Patent 2025/128,348 (thermoacoustic meta-structure, NASA Langley collaboration) + 1 active invention disclosure as lead inventor
- Built and managed a $300K+ instrumented acoustic test facility

## Open-source engineering tools

Small, readable, and tested against physics rather than just execution. Every
README states the limits as plainly as the results.

| Repository | What it proves |
|---|---|
| [**pinn-acoustics**](https://github.com/Samarjithbiswas/pinn-acoustics) | A PyTorch PINN solves the acoustic wave equation with *zero* solution data (3.9% max error) and recovers a hidden wave speed from 80 noisy points to **0.08%** |
| [**fem-surrogate-toolkit**](https://github.com/Samarjithbiswas/fem-surrogate-toolkit) | The full surrogate pipeline: Latin-hypercube DoE → POD compression → ridge. Predicts a 128-point spectrum in **~3 µs/design** at held-out R² ≈ 0.95 |
| [**phononic-bands**](https://github.com/Samarjithbiswas/phononic-bands) | Bloch-Floquet band structures in pure NumPy/SciPy. Reproduces the steel-in-epoxy benchmark gap; tests check analytic sound speed and reciprocal-space periodicity |
| [**saw-device-sim**](https://github.com/Samarjithbiswas/saw-device-sim) | Analytic IDT + transfer-matrix models of surface-acoustic-wave devices, validated to **0.3%** against a published measured device |
| [**modal-correlation**](https://github.com/Samarjithbiswas/modal-correlation) | MAC, mode pairing, and COMAC: the unglamorous glue that decides whether your FEA actually matches the bench |

## Toolbox

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)
![ONNX](https://img.shields.io/badge/ONNX-005CED?style=flat&logo=onnx&logoColor=white)
![MATLAB](https://img.shields.io/badge/MATLAB-E16737?style=flat)
![COMSOL](https://img.shields.io/badge/COMSOL_Multiphysics-368CCB?style=flat)
![ANSYS](https://img.shields.io/badge/ANSYS-FFB71B?style=flat&logoColor=black)
![SolidWorks](https://img.shields.io/badge/SolidWorks-DB0000?style=flat)
![LabVIEW](https://img.shields.io/badge/LabVIEW_/_NI--DAQ-FFDB00?style=flat&logoColor=black)

Simulation: COMSOL (acoustics, solid mechanics, Bloch-Floquet), ANSYS (Mechanical/Fluent) ·
ML: physics-informed networks, 3D CNNs, reduced-order surrogates, ONNX-to-browser deployment ·
Lab: anechoic/reverberation chambers, impedance tube, laser-Doppler vibrometry, modal testing

## What I'm looking at now

Physics-AI: the space where a trained network replaces a solver inside a real
engineering workflow, and the validation discipline that makes that trustworthy.
If you're working on simulation surrogates, acoustic devices, or
structural-dynamics correlation, my inbox is open.

<div align="center">

*"A surrogate is not a solver, a 1D model is not an FEM, and knowing exactly
which one you're holding is most of the job."*

</div>
