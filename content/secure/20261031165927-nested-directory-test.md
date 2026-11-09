---
title: "Nested Dir Test"
date_edtf: "2026-10-31T16:59:27"
keywords: ["delete"]
---

# Nested Directory And Encryption Testing

This is a test of markdown, media, and math encryption compatibility.

## Media Encryption

![Test - Artemis II](media/test_artemis_2.jpg)

***

## Math Testing (KaTeX)

### Single Complex Equation

$$\mathrm{i\hbar \frac{\partial}{\partial t} \Psi(\mathrm{r}, t) = \left[ -\frac{\hbar^2}{2m} \nabla^2 + V(\mathrm{r}, t) \right] \Psi(\mathrm{r}, t)}$$

### Delimiter Syntax Variations

Inline with single dollar: The energy-momentum relation is $E^2 = (pc)^2 + (m_0 c^2)^2$ where $c$ is the speed of light.

Inline with LaTeX parens are **not allowed**.

Display with double dollars:
$$\nabla \times \mathbf{B} = \mu_0 \left( \mathbf{J} + \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t} \right)$$

Display with LaTeX brackets is **not allowed**.

### Multiline Environments and Alignment

Aligned system of equations (testing multiline internal parsing without delimiter breakage):

$$
\begin{aligned}
\nabla \cdot \mathbf{E} &= \frac{\rho}{\varepsilon_0} \\
\nabla \cdot \mathbf{B} &= 0 \\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \times \mathbf{B} &= \mu_0 \mathbf{J} + \mu_0 \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}
\end{aligned}
$$

Piecewise definitions (cases):

$$
f(x) = \begin{cases} 
\frac{\sin x}{x} & \text{if } x \neq 0, \\
1 & \text{if } x = 0.
\end{cases}
$$

### Matrices and Tensors

Matrix with brackets and fractions:

$$
\mathbf{U} = \frac{1}{\sqrt{2}}
\begin{bmatrix}
1 & 0 & 1 & 0 \\
0 & 1 & 0 & 1 \\
1 & 0 & -1 & 0 \\
0 & 1 & 0 & -1
\end{bmatrix}
$$

Determinant and Pauli matrices:

$$
\det(\sigma_z) = 
\begin{vmatrix}
1 & 0 \\
0 & -1
\end{vmatrix}
= -1
$$

### Advanced Limits, Integrals, and Sums

Gaussian integral identity with limits:

$$
\int_{-\infty}^{+\infty} e^{-a x^2} \, dx = \sqrt{\frac{\pi}{a}} \quad (a > 0)
$$

Summation with limits and binomial coefficients:

$$
\sum_{k=0}^{n} \binom{n}{k} x^k a^{n-k} = (x + a)^n
$$

Contour integral with residues:

$$
\oint_{C} f(z) \, dz = 2\pi i \sum_{k=1}^{n} \operatorname{Res}(f, a_k)
$$

### Tagging, Text, and Accents

Display equation with custom tag:

$$
\mathcal{L} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu} \tag{QED}
$$

Inline mixed text, accents, and symbols:
Let $\hat{a}^\dagger$ and $\hat{a}$ be creation and annihilation operators such that $[\hat{a}, \hat{a}^\dagger] = 1$, with expectation value $\langle \psi | \hat{H} | \psi \rangle \ge E_0$.
