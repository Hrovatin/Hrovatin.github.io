---
title: "Correcting technical artifacts: The case of ambient gene expression"
#date: YYYY-MM-DD HH:MM:SS +/-TTTT
categories: [Data analysis]
tags: [single-cell, technical effects, correction]     # TAG names should always be lowercase
description: There are many ways to crack a nut, but without the right tool none are easy.
media_subpath: /assets/img/2024-11-11-ambient_expression/
image:
  path: stormy_sea_preview.png
  alt: <b>A fight against ambient expression.</b><br>On a stormy sea "of ambient gene expression" a scientist is bailing out water (ambient expression) from his sinking boat (sequencing droplet containing a cell).
---

In this blog post, I will discuss the limitations of commonly used methods 
for correcting a technical artifact known as ambient gene expression (AGE). 
Although this artifact is specific to single-cell transcriptome sequencing 
(scRNA-seq) data, the approaches for its modeling and mitigation share 
considerations with artifact removal and domain adaptation in other data types. 
Those in the single-cell field may recognize AGE a component of “batch effects”.

_The limitations of the AGE correction methods discussed in this blog post are 
largely based on my own experience. The AGE biases were one of my greatest 
enemies while analyzing my scRNA-seq pancreatic atlas (Hrovatin, 2023), 
especially when interpreting differential gene expression (DE) results. 
Thus, I tried out various correction methods. I tested multiple correction 
tools (SoupX, DecontX, and CellBender) in the autumn of 2020 and later 
alternative approaches for mitigating AGE. For this blog post, I again 
reviewed the literature in the autumn of 2024._ 

_While I discuss the solutions on which I decided, I must admit that I am 
not fully satisfied with them. - So do not consider them as set in stone, 
but rather as something to ponder over._

<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">
The first few sections introduce ambient expression and its relevance 
for different data analysis applications. If you are already very familiar 
with ambient expression and scRNA-seq data, you can skip most of the 
early sections with <strong style="color:#0c739c;">blue</strong> titles 
and instead focus on sub-sections with <strong>black</strong> 
titles, where I discuss my observations.
</div>

## <span style="color:#0c739c;">What is ambient expression?</span>

![Desktop View](ambient_expression.jpg){: width="800" alt="abc" .shadow;}
_<b>Figure 1:</b> text_

![Desktop View](ambient_correction.jpg){: width="450" alt="abc" .shadow;}
_<b>Figure 2:</b> text_

![Desktop View](ambient_variation.jpg){: width="350" alt="abc" .shadow;}
_<b>Figure 3:</b> text_

![Desktop View](within_between_batch.jpg){: width="400" alt="abc" .shadow;}
_<b>Figure 4:</b> text_

![Desktop View](estimated_contamination.jpg){: width="400" alt="abc" .shadow;}
_<b>Figure 5:</b> text_

![Desktop View](relative_expr.jpg){: width="600" alt="abc" .shadow;}
_<b>Figure 6:</b> text_


text[^footnote1]

text[^footnote2]

## Acknowledgements

The ideas presented in this blog post stem from discussions with my former 
colleagues at Helmholtz Munich, particularly my mentors Maren Büttner and 
Luke Zappia. I got some suggestions regarding DE tools from 
Soroor Hediyeh-zadeh and Alejandro Tejada Lapuerta helped to review the post.

## References

- Berg, M., et al. FastCAR: fast correction for ambient RNA to facilitate 
differential gene expression analysis in single-cell RNA-sequencing datasets. 
BMC Genomics (2023).
- Fleming, S. J., et al. Unsupervised removal of systematic background noise 
from droplet-based single-cell experiments using CellBender. Nat Methods (2023).
- Hrovatin, K., et al. Delineating mouse β-cell identity during lifetime and 
in diabetes with a single cell atlas. Nat Metab (2023).
- Janssen, P., et al. The effect of background noise and its removal on the 
analysis of single-cell expression data. Genome Biol (2023).
- Yang, S., et al. Decontamination of ambient RNA in single-cell RNA-seq with 
DecontX. Genome Biol (2020).
- Young, M. D., et al. SoupX removes ambient RNA contamination from 
droplet-based single-cell RNA sequencing data. GigaScience (2020).

## Footnotes

[^footnote1]: As the information captured by individual genes is redundant, cell representations are commonly computed on a subset of genes. Thus, genes that may contribute less to cross-batch differences can be prioritized. 

[^footnote2]: To be precise, AGE should be incorporated as an offset variable rather than a normal predictor variable. However, explaining this is beyond the scope of this post. See [this discussion](https://stats.stackexchange.com/questions/175349/in-a-poisson-model-what-is-the-difference-between-using-time-as-a-covariate-or) for more information.
