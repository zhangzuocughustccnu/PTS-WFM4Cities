# Method conventions

## Analytical surface

WFM4Cities represents one explicitly defined urban attribute as a single-valued
regular surface \(z_r\). Scattered observations can be interpolated with SciPy's
cubic `griddata`; nearest-neighbor interpolation fills cells outside the
cubic convex hull. The maintained workflow then applies min--max normalization
when relative morphology is the target of comparison.

## Progressive Threshold Scanning

For a fixed domain with \(M\) cells and threshold \(h\), the retained
superlevel set is either:

\[
\Omega(h)=\{r:z_r\ge h\}
\]

for the inclusive rule, or:

\[
\Omega(h)=\{r:z_r>h\}
\]

for the strict rule.

The four response metrics are:

\[
A(h)=\frac{1}{M}\sum_{r=1}^{M}\mathbf{1}(z_r\ \text{passes}\ h)
\]

\[
V(h)=\frac{\sum_{r=1}^{M}\max(z_r-h,0)}
{\sum_{r=1}^{M}z_r}
\]

\[
N(h)=\text{number of connected components in }\Omega(h)
\]

\[
L(h)=\frac{\text{cells in the largest component}}
{\text{cells in }\Omega(h)}
\]

and \(L(h)=0\) when no cell is retained.

The default scan uses 51 thresholds from 0 to 0.95 and eight-neighbor
connectivity. The inclusive rule matches the controlled archetype workflow.
The strict rule is intended for a fully finite grid in which zero is background
and must be excluded at \(h=0\).

## Fixed ten-feature summary

`extract_features` returns:

1. \(V(0.2)\);
2. \(A(0.2)\);
3. \(A(0.4)\);
4. \(A(0.6)\);
5. \(V(0.4)\);
6. \(L(0.4)\);
7. \(N(0.4)\);
8. normalized AUC of \(L(h)\);
9. normalized AUC of \(V(h)\);
10. the interpolated threshold at which \(A(h)\) first falls below 0.10.

Continuous features at unsampled thresholds use linear interpolation.
\(N(0.4)\) uses the nearest sampled threshold. AUC uses trapezoidal
integration divided by the scanned threshold width.

## Interpretation boundary

PTS measures how a scalar surface responds to threshold changes. It does not
simulate fluid motion, historical change, causal processes, or network flows.
Absolute cross-city interpretation additionally requires compatible units,
domains, coordinate systems, spatial resolution, and metadata.
