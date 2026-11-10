---
title: Mathematical Typesetting & Edge-Case Escapes
date_edtf: 2026-12-01
keywords: katex, mathematics, latex, calculus, chemistry, mhchem
description: Exhaustive validation of inline and block math formatting, symbols, and chemical equations.
---

# Mathematical Typesetting & Edge-Case Escapes

This document exercises the KaTeX rendering pipeline and mathematical delimiters.

## 1. Inline Mathematics

The Euler-Lagrange equation in classical mechanics is given by:
$\frac{d}{dt} \left( \frac{\partial L}{\partial \dot{q}_i} \right) - \frac{\partial L}{\partial q_i} = 0$, where $L = T - V$ represents the Lagrangian.

Another inline example with brackets: \(\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}\).

Inline math with matrix notation: $A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$.

## 2. Display Mathematics

The divergence theorem states:

$$
\iiint_V (\mathbf{\nabla} \cdot \mathbf{F}) \, dV = \iint_S (\mathbf{F} \cdot \mathbf{\hat{n}}) \, dS
$$

The Schrödinger equation in one dimension:

\[
i\hbar \frac{\partial}{\partial t} \Psi(x,t) = \left[ -\frac{\hbar^2}{2m} \frac{\partial^2}{\partial x^2} + V(x,t) \right] \Psi(x,t)
\]

A multi-line derivation using the `aligned` environment:

$$
\begin{aligned}
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \times \mathbf{B} &= \mu_0 \mathbf{J} + \mu_0 \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t} \\
\nabla \cdot \mathbf{E} &= \frac{\rho}{\varepsilon_0} \\
\nabla \cdot \mathbf{B} &= 0
\end{aligned}
$$

## 3. Chemical Formulae (mhchem)

Kykloi assets include KaTeX's `mhchem` extension. Verify if chemical notation parses:

$$\ce{2H2 + O2 -> 2H2O}$$

$$\ce{^{227}_{90}Th ->[ \alpha ] ^{223}_{88}Ra ->[ \alpha ] ^{219}_{86}Rn}$$

## 4. Special Characters and Escaped Characters

* Asterisks that are not bold: \*literal asterisks\*
* Backticks that are not code: \`literal backtick\`
* Math delimiters in regular text: Price is $5.00 for item A and $10.00 for item B (must not parse as math).
