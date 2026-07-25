<div align="center">

![header](https://capsule-render.vercel.app/api?type=waving&height=200&color=gradient&customColorList=6,17,27&text=Samarjith%20Biswas,%20Ph.D.&fontSize=42&fontColor=ffffff&animation=fadeIn&desc=Physics%20%E2%80%A2%20Simulation%20%E2%80%A2%20Machine%20Learning&descSize=18&descAlignY=75)

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=800&color=00A8B5&center=true&vCenter=true&width=650&lines=I+make+physics+simulation+fast+enough+to+design+with;3-hour+FEM+solves+%E2%86%92+5-millisecond+predictions;Acoustic+metamaterials+%E2%80%A2+PINNs+%E2%80%A2+validated+surrogates;Model+it.+Build+it.+Measure+it.+Make+them+agree.)](https://samarjithbiswas.com)

**Research Scientist III · NewFoS Center, University of Arizona**
Ph.D. Mechanical & Aerospace Engineering · Topological acoustics, wave physics, and machine learning

[![Website](https://img.shields.io/badge/samarjithbiswas.com-005F73?style=for-the-badge&logo=googlechrome&logoColor=white)](https://samarjithbiswas.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/samarjithbiswas/)
[![Google Scholar](https://img.shields.io/badge/Scholar-4285F4?style=for-the-badge&logo=googlescholar&logoColor=white)](https://scholar.google.com/citations?user=EyxF_uoAAAAJ)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:samarjithbiswas@arizona.edu)

</div>

## 🌊 The one-paragraph version

A finite-element solve of a phononic crystal takes one to three hours. I built
[**PhononIQ**](https://samarjithbiswas.github.io/phononiq/), a physics-informed
deep-learning surrogate that gives the same answer in about **5 milliseconds**
at R² ≈ 0.98, running in your browser. Getting there meant owning every layer:
thousands of automated simulations for training data, network architectures
designed around the physics, loss functions that cut unphysical predictions by
**57%**, and validation against ground truth before believing any of it. The
same discipline runs through everything below: model it, build it, measure it,
and make the model and the measurement agree, currently to within **±2%**.

## 🏆 Proof points

| | |
|---|---|
| 📄 | **Lead author, *Scientific Reports* (2026)** — directional interface modes in topological acoustic metamaterials, with A. Alù (CUNY/ASRC) & M. Leamy (Georgia Tech) · [DOI](https://doi.org/10.1038/s41598-026-62783-x) |
| 📄 | **Co-author, *Physical Review Applied* 25, 054035 (2026)** — composite superlattice SAW RF devices |
| 🔬 | **US Patent 2025/128,348** — thermoacoustic meta-structure (NASA Langley collaboration) + 1 active invention disclosure as lead inventor |
| 🏗️ | Built and managed a **$300K+** instrumented acoustic test facility (anechoic + reverberation chambers, laser-Doppler vibrometry) |

## 🛠️ Open-source engineering tools

Small, readable, and tested against **physics**, not just execution. Every README states the limits as plainly as the results.

| Repository | What it proves |
|---|---|
| 🧠 [**pinn-acoustics**](https://github.com/Samarjithbiswas/pinn-acoustics) | A PyTorch PINN solves the wave equation with *zero* solution data (3.9% max error) and recovers a hidden wave speed from 80 noisy points to **0.08%** |
| ⚡ [**fem-surrogate-toolkit**](https://github.com/Samarjithbiswas/fem-surrogate-toolkit) | The full surrogate pipeline: Latin-hypercube DoE → POD compression → ridge. A 128-point spectrum in **~3 µs/design** at held-out R² ≈ 0.95 |
| 🎵 [**phononic-bands**](https://github.com/Samarjithbiswas/phononic-bands) | Bloch-Floquet band structures in pure NumPy/SciPy; reproduces the steel-in-epoxy benchmark gap with physics-checked tests |
| 📡 [**saw-device-sim**](https://github.com/Samarjithbiswas/saw-device-sim) | Analytic IDT + transfer-matrix models of SAW devices, validated to **0.3%** against a published measured device |
| 📊 [**modal-correlation**](https://github.com/Samarjithbiswas/modal-correlation) | MAC, mode pairing, and COMAC: the unglamorous glue that decides whether your FEA actually matches the bench |

## 🧰 Toolbox

<div align="center">

[![Skills](https://skillicons.dev/icons?i=python,pytorch,tensorflow,matlab,js,threejs,docker,git,linux,latex&theme=dark)](https://skillicons.dev)

![COMSOL](https://img.shields.io/badge/COMSOL_Multiphysics-368CCB?style=for-the-badge)
![ANSYS](https://img.shields.io/badge/ANSYS-FFB71B?style=for-the-badge&logoColor=black)
![ONNX](https://img.shields.io/badge/ONNX-005CED?style=for-the-badge&logo=onnx&logoColor=white)
![SolidWorks](https://img.shields.io/badge/SolidWorks-DB0000?style=for-the-badge)
![LabVIEW](https://img.shields.io/badge/LabVIEW_/_NI--DAQ-FFDB00?style=for-the-badge&logoColor=black)

</div>

**Simulation** · COMSOL (acoustics, solid mechanics, Bloch-Floquet), ANSYS (Mechanical/Fluent) &nbsp;|&nbsp;
**ML** · physics-informed networks, 3D CNNs, reduced-order surrogates, ONNX-to-browser deployment &nbsp;|&nbsp;
**Lab** · anechoic/reverberation chambers, impedance tube, laser-Doppler vibrometry, modal testing

## 📈 GitHub at a glance

<div align="center">

<img height="165" src="https://github-readme-stats.vercel.app/api?username=Samarjithbiswas&show_icons=true&hide_border=true&title_color=00A8B5&icon_color=00A8B5&text_color=8b949e&bg_color=00000000" alt="stats" />
<img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username=Samarjithbiswas&layout=compact&hide_border=true&title_color=00A8B5&text_color=8b949e&bg_color=00000000&langs_count=8" alt="languages" />

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Samarjithbiswas/Samarjithbiswas/output/github-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Samarjithbiswas/Samarjithbiswas/output/github-snake.svg" />
  <img alt="contribution snake" src="https://raw.githubusercontent.com/Samarjithbiswas/Samarjithbiswas/output/github-snake.svg" />
</picture>

</div>

## 🔭 What I'm looking at now

**Physics-AI**: the space where a trained network replaces a solver inside a
real engineering workflow, and the validation discipline that makes that
trustworthy. If you're working on simulation surrogates, acoustic devices, or
structural-dynamics correlation, my inbox is open.

<div align="center">

*"A surrogate is not a solver, a 1D model is not an FEM, and knowing exactly
which one you're holding is most of the job."*

![footer](https://capsule-render.vercel.app/api?type=waving&height=100&color=gradient&customColorList=6,17,27&section=footer)

</div>
