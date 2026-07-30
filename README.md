<div align="center">

<img src="assets/hero.svg" alt="Samarjith Biswas, Ph.D. — Research Scientist III, NewFoS Center, University of Arizona" width="100%">

<br>

[![Website](https://img.shields.io/badge/samarjithbiswas.com-005F73?style=flat-square&logo=googlechrome&logoColor=white)](https://samarjithbiswas.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/samarjithbiswas/)
[![Google Scholar](https://img.shields.io/badge/Google_Scholar-4285F4?style=flat-square&logo=googlescholar&logoColor=white)](https://scholar.google.com/citations?user=EyxF_uoAAAAJ)
[![Email](https://img.shields.io/badge/samarjithbiswas@arizona.edu-D14836?style=flat-square&logo=maildotru&logoColor=white)](mailto:samarjithbiswas@arizona.edu)

</div>

---

A finite-element solve of a phononic crystal takes one to three hours. I build the
surrogates that answer the same question in milliseconds, and the validation
discipline that makes the answer worth acting on.

That means owning the whole chain rather than one link in it: thousands of automated
simulations to generate training data, network architectures chosen around the
physics rather than around fashion, loss functions that penalise physically
impossible predictions, laser-vibrometer measurements on fabricated hardware, and a
comparison at the end that either agrees or gets explained. Currently that agreement
runs to within **±2%** on measured band edges.

I am equally interested in where these methods fail, because that is what decides
whether a surrogate belongs in a design loop or only in a paper.

## Selected record

| | |
|---|---|
| **Publication** | Lead author, *Scientific Reports* (2026). Directional interface modes in topological acoustic metamaterials, with A. Alù (CUNY ASRC) and M. Leamy (Georgia Tech). [10.1038/s41598-026-62783-x](https://doi.org/10.1038/s41598-026-62783-x) |
| **Publication** | Co-author, *Physical Review Applied* **25**, 054035 (2026). Composite superlattice surface-acoustic-wave RF devices. |
| **Patent** | US 2025/128,348, thermoacoustic meta-structure, in collaboration with NASA Langley. Plus one active invention disclosure as lead inventor. |
| **Facility** | Specified, built and ran a **$300K+** instrumented acoustic laboratory: anechoic and reverberation chambers, impedance tube, laser-Doppler vibrometry, modal testing. |
| **Funding** | Work supported under NSF NewFrontiers of Sound (NewFoS) award #2242925. |

## What the work looks like

Every figure below is plotted from data on disk. Nothing here is an illustration, and
the code that produces them is in [`assets/make_real_figures.py`](assets/make_real_figures.py).

<div align="center">
<img src="assets/drivaer_geometry.png" alt="Three real DrivAerNet++ surface point clouds with their measured drag coefficients" width="100%">
</div>

Real 8,000-point CFD surface clouds from DrivAerNet++, spanning measured drag from
0.2192 to 0.3164. This is the actual input a geometric deep-learning surrogate consumes:
an unordered point cloud with no mesh connectivity, which is why a dynamic-graph
architecture that builds its own neighbourhoods is the right tool rather than a
convolutional one.

<div align="center">
<img src="assets/training.png" alt="Real 50-epoch training curve of the drag surrogate: validation R-squared and MAE" width="86%">
</div>

The real training log. Validation R² climbs from 0.26 to **0.809** and drag-coefficient
MAE falls from 0.0175 to **0.0082**, on 825 held-out cars at 2,048 sampled points each.

The caveats belong in the same breath as the number. That is a validation curve used for
checkpoint selection, not a sealed test result, and the split is random rather than the
authors' published one. The model was trained at 2,048 points; evaluating the same
weights at 5,000 points drops R² to roughly 0.59, which is a concrete lesson in why
discretisation invariance is the property to care about in operator learning. The
wall-shear-stress head is far weaker than the drag head.

<div align="center">
<img src="assets/dataset.png" alt="Measured drag distribution across 8,121 DrivAerNet++ CFD runs" width="86%">
</div>

Why that error figure means anything: across 8,121 runs the drag coefficient has a
standard deviation of 0.0201, so an MAE of 0.0082 is **0.41 standard deviations**. An R²
quoted without the spread of its test set is not a claim, and this is the plot that makes
it one.

<sub>Geometry and drag data from **DrivAerNet++** (Elrefaie, Dai and Ahmed), used here for
non-commercial research under its licence. The point clouds and drag coefficients are
theirs; the surrogate, the training run and these plots are mine.</sub>

## Open-source engineering tools

Small, readable, and tested against physics rather than merely against execution.
Every README states the limits as plainly as the results.

| Repository | What it demonstrates |
|---|---|
| [**neuralmesh**](https://github.com/Samarjithbiswas/neuralmesh) | Does global attention fix under-reaching in mesh graph networks? A controlled measurement: parameter counts matched to 0.7%, a no-communication control, and error resolved by distance from the boundary. Ground truth is a P1 FEM solver verified to **second order** (measured rates 1.947 and 1.987). 72 tests, CI on three Python versions |
| [**AcousticPINN**](https://github.com/Samarjithbiswas/AcousticPINN) | A PyTorch physics-informed network solves the wave equation with *zero* solution data at 3.9% maximum error, and recovers a hidden wave speed from 80 noisy points to **0.08%** |
| [**FEMSurrogateToolkit**](https://github.com/Samarjithbiswas/FEMSurrogateToolkit) | The full surrogate pipeline: Latin-hypercube design of experiments, POD compression, ridge regression. A 128-point spectrum in about **3 µs per design** at held-out R² ≈ 0.95 |
| [**PhononicBands**](https://github.com/Samarjithbiswas/PhononicBands) | Bloch-Floquet band structures in pure NumPy and SciPy, reproducing the steel-in-epoxy benchmark gap with physics-checked tests |
| [**SAWDeviceSim**](https://github.com/Samarjithbiswas/SAWDeviceSim) | Analytic interdigital-transducer and transfer-matrix models of SAW devices, validated to **0.3%** against a published measured device |
| [**ModalCorrelation**](https://github.com/Samarjithbiswas/ModalCorrelation) | MAC, mode pairing and COMAC: the unglamorous work that decides whether an FE model actually matches the bench |
| [**CFDSurrogate**](https://github.com/Samarjithbiswas/CFDSurrogate) | Graph neural network surrogate for airfoil flow fields, with a runnable demo |
| [**ChatCAD**](https://github.com/Samarjithbiswas/ChatCAD) | Chat-driven parametric CAD on a real OpenCascade B-rep kernel, with a multi-agent design loop and FEA on the same geometry |

## Where I am strong

**Simulation.** COMSOL Multiphysics for acoustics, solid mechanics and Bloch-Floquet
eigenvalue problems. ANSYS Mechanical and Fluent. Verification by mesh convergence
and closed-form comparison, not by inspection.

**Machine learning.** Physics-informed networks, 3D convolutional and graph
architectures, neural operators, reduced-order and POD surrogates, ONNX export to
run models in a browser. PyTorch.

**Measurement.** Anechoic and reverberation chambers, impedance tube, laser-Doppler
vibrometry, modal testing and correlation. The half of the job that decides whether
the other half was real.

**Fabrication.** Laser-machined borosilicate phononic plates, from design through to
a measured transmission spectrum.

## Currently

Physics-AI: the point where a trained model genuinely replaces a solver inside a
real engineering workflow, and the evidence required before anyone should let it.
If you work on simulation surrogates, acoustic or RF devices, or structural-dynamics
correlation, I am glad to talk.

<div align="center">

<br>

*A surrogate is not a solver, a one-dimensional model is not an FE model,*
*and knowing exactly which one you are holding is most of the job.*

</div>
