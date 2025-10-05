---
icon: fas fa-archive
order: 4
media_subpath: /assets/img/insights/
---

The most unexpected and/or useful data science bits I have learned in the past weeks. 

This page serves as an archive of these updates.

## Sources of variation

The strongest source of variation in protein property prediction (in a low-data regime) seem to be protein representations, rather than classical ensemble-building techniques (e.g., different random seeds or data splits for training).

![Desktop View](20250827.jpeg){: width="600" alt="Protein representations present one of the strongest sources of variation for property prediction." .shadow style="border-radius: 7px;"}
_2025-08-27_

## Biases in uncertainty estimates

The relatively uncertainty of regions away from training data can be underestimated. One of the reasons behind this may be a combination of underfitting in regions away from data, which may result in more uniform predictions across models within an ensemble, and overfitting in regions close to the data, leading to higher variability across ensemble members.

![Desktop View](20250715.jpeg){: width="600" alt="The relatively uncertainty of regions away from training data can be underestimated." .shadow style="border-radius: 7px;"}
_2025-07-15_

## CLS token representation biases

When using CLS token as protein representations, the mutations in certain regions of protein sequence may be over-prioritized.

![Desktop View](20250701.jpeg){: width="600" alt="When using CLS token as protein representations, the mutations in certain regions of protein sequence may be over-prioritized." .shadow style="border-radius: 7px;"}
_2025-07-01_



