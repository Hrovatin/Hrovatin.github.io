---
title: "Correcting technical artifacts: The case of ambient gene expression"
date: 2024-12-15 00:00:00
last_modified_at: 2024-12-15 00:00:00
categories: [Data analysis]
tags: [single-cell, technical biases, data correction]     # TAG names should always be lowercase
description: There are many ways to crack a nut, but without the right tool none are easy.
media_subpath: /assets/img/2024-11-11-ambient_expression/
image:
  path: stormy_sea_preview.png
  alt: <b>A fight against ambient expression.</b><br>On a stormy sea "of ambient gene expression" a scientist is bailing out water (ambient expression) from his sinking boat (sequencing droplet containing a cell).
---

{% include toggle-details.html %}

In this blog post, I will discuss the limitations of commonly used methods 
for correcting a technical artifact known as ambient gene expression (AGE). 
Although this artifact is specific to single-cell transcriptome sequencing 
(scRNA-seq) data, the approaches for its modeling and mitigation resemble
domain correction and adaptation approaches used for other data types. 
Those in the single-cell field may recognize AGE as a component of “batch effects”.

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
early sections with <strong style="color:#c96f00;">orange</strong> titles 
and instead focus on sub-sections with <strong>black</strong> 
titles, where I discuss my observations.
</div>

<br>

<details closed>
<summary><u>Sections list</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">
<ul>
<li><span style="color:#c96f00;">What is ambient expression?</span></li>
<li><span style="color:#c96f00;">Methods for AGE correction</span></li>
<li>Aligning AGE correction methods with downstream data use cases</li>
<li>AGE correction as a pre-processing step for data integration</li>
<li>Challenges of AGE correction for DE analysis</li>
<ul>
<li><span style="color:#c96f00;">Effect of AGE on DE analysis</span></li>
<li>Limitations of AGE correction methods for cross-batch comparison</li>
<li>Removing likely ambient genes from DE analysis</li>
<li>Excluding genes whose DE can be explained by ambient DE</li>
</ul>
</ul>
</div>
</details>

## <span style="color:#c96f00;">What is ambient expression?</span>

It is important to understand the general characteristics of AGE (**Figure 1**) 
as they are used as inductive biases in AGE correction approaches. 

<details closed>
<summary><u>Brief introduction of scRNA-seq</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">
In the following text, I will use scRNA-seq terminology, which can be 
translated to general machine-learning terms as follows: 
<ul>
<li> Cells and droplets are samples.</li>
<li> Batches or sequencing samples are domains.</li>
<li> Genes or their transcripts are features.</li>
</ul>
To assess the molecular characteristics of individual cells, the activity of 
each gene (i.e. “template” for specific molecular function) is quantified via 
sequencing, measuring the number of transcribed RNA molecules
(corresponding to the number of “tools” for specific molecular function). 
To enable sequencing of individual cells, the cells are encapsulated in 
lipid droplets.
<br><br>
Tissues contain multiple classes of cells with similar functions and gene 
expression, called cell types. However, the gene expression of two cells 
from the same cell type will never be the same due to:
<ul>
<li> The noisiness of biochemical reactions 
(i.e. probabilistic nature of gene expression). </li>
<li> Underlying biological differences, which depend on cell type annotation 
resolution. </li>
<li> Technical effects. </li>
</ul>
</div>
</details>
<br>

![Desktop View](ambient_expression.jpg){: width="850" alt="Overview of ambient gene expression properties." .shadow style="border-radius: 7px;"}
_**Figure 1: Properties of ambient gene expression.**_

Summary of AGE characteristics:
- **Data of each cell can be, in theory, decomposed into endogenous (true) 
and exogenous (ambient artifact) components[^footnote1].** 
  - Cause of AGE: Besides the cell and its endogenous transcripts, 
  each droplet will also contain some of the liquid in which cells are 
  dispersed during sample preparation. As some of the cells burst during 
  processing, their RNA will be released in the solution and subsequently 
  captured within droplets, representing the exogenous “ambient” RNA.
- **The underlying AGE distribution is shared across all droplets processed in 
the same batch (e.g. test tube), but the final measured AGE differs between 
droplets.**
  - Shared distribution: Every test tube contains multiple cells that will 
  be encapsulated into droplets, and for them, the exogenous molecules that 
  are captured within the droplet are sampled from the same distribution. 
  - Observation differences: The measured AGE will differ across cells for 
  several reasons: First, the ambient transcripts captured in each droplet 
  will vary due to sampling randomness. Second, the relative number of exogenous 
  transcripts compared to the endogenous transcripts will be affected by 
  cell-specific factors, such as cell size. 
- **Droplets of cells that truly express a gene will have higher counts for 
that gene than droplets of cells that do not express that gene, 
containing only exogenous transcripts.**
- **Some cells have similar endogenous expressions.**
  - Joint modeling: Biologically related cells are expected to share the 
  underlying distributions from which the measured endogenous as well as 
  exogenous transcripts are sampled. Thus, gene expression characteristics 
  can be modeled jointly in similar cells. 
- **The underlying AGE distribution can be estimated from the data.** 
  - Empty droplets: Some of the measured droplets will contain no cells and 
  they can be 
  identified by a low number of transcripts. The transcripts within 
  these droplets thus represent AGE within the batch.
- **The composition of AGE strongly depends on cell type 
proportions within the batch.**
  - Deviation from cell type proportion relationship: 
  Cells from different cell types have distinct AGE contribution properties. 
  For example, they differ in the likelihood of bursting and cell size, 
  which determines the number of transcripts released into the solution 
  upon bursting. Thus, AGE distribution cannot be directly approximated by 
  cell type proportions.

## <span style="color:#c96f00;">Methods for AGE correction</span>

Various AGE correction tools have been developed to produce expression data 
free of AGE contamination, including SoupX (Young, 2020), DecontX (Yang, 2020), 
CellBender (Fleming, 2023), and FastCAR (Berg, 2023). 
The AGE correction is usually performed in two steps (**Figure 2**): 
1. Estimate AGE within a batch, commonly based on empty droplets, 
as explained above. 
2. Using the estimated AGE, decompose the expression of every cell into 
exogenous and corrected endogenous expression. The latter is then used 
for downstream analysis. 

![Desktop View](ambient_correction.jpg){: width="500" alt="Overview of ambient gene expression correction approach used in most correction tools." .shadow style="border-radius: 7px;"}
_**Figure 2: Overview of ambient gene expression correction approach used in most tools.**_

The modeling approaches used in AGE correction tools differ in multiple 
aspects, such as:
- The fraction of all exogenous vs endogenous transcripts within droplets 
(i.e. contamination fraction) can be: 
  - Directly estimated from the data (Young, 2020).
  - Incorporated into a model as a learnable parameter 
  (Yang, 2020; Fleming, 2023).
- The number of exogenous transcripts of a gene can be:
  - Estimated only on a per-batch level, being fixed across 
  droplets (Berg, 2023).
  - Modeled on a per-droplet level (Yang, 2020; Young, 2020; Fleming, 2023).
- The droplets can be:
  - Treated independently (Berg, 2023).
  - Expression information can be shared across biologically similar cells 
  (e.g. cell types) (Yang, 2020; Young, 2020; Fleming, 2023). 
  Biologically similar cells can be defined based on discrete cluster 
  membership (Yang, 2020; Young, 2020) or location in continuous 
  transcriptome-based representation space (e.g. cell embedding) 
  (Fleming, 2023).

In addition to the AGE correction tools described above, other alternatives 
primarily focused on DE analysis are discussed by Amezquita (2021). Briefly, 
this includes excluding genes whose expression levels are predominately 
affected by AGE from downstream analysis or eliminating genes whose DE is 
likely driven by AGE. These two approaches are also further discussed below.

## Aligning AGE correction methods with downstream data use cases

When planning ambient correction, it is crucial to consider which downstream 
analysis the corrected data will be used for. Namely, each ambient correction 
method has its limitations, which can impact various types of analyses 
differently. For example:
- Some use cases require accurate correction of individual genes, 
such as for detecting DE genes between specific biological conditions or for 
identifying markers of individual cell populations. On the other hand, 
certain applications require only mitigating the largest AGE differences to 
reduce the biases within cell representations, such as for cell clustering or 
data integration. 
- Some analyses are performed on a per-batch level, meaning that AGE 
correction must be truthful and comparable across cells within a batch. 
However, many analyses include multiple batches, which means that AGE 
correction must also be comparable across batches.

In my experience, conducting gene-level cross-batch analysis on AGE-corrected 
data is the most challenging application, as discussed below. I will 
illustrate this with examples from data integration and DE analysis, the 
two areas where I investigated AGE correction in more detail.

## AGE correction as a pre-processing step for data integration

AGE correction reduces technical variation between batches, enabling the 
creation of a common representation space (i.e. embedding) where batches 
are more closely aligned. This process is typically referred to as batch 
correction or integration in the scRNA-seq community. Besides, AGE correction 
can serve as a pre-processing step before applying dedicated integration 
methods, which aim to correct for diverse technical effects. By removing 
a portion of the technical variation (i.e. AGE), the downstream 
integration becomes easier. 

In this setting, I observed that removing the major ambient effects can 
already lead to relatively strong improvement. For example, simply excluding 
the genes with the highest AGE from the features used to compute the 
integrated representation[^footnote2] can achieve performance comparable to 
that of dedicated AGE correction tools (Hrovatin, 2023). However, it is 
important to note that if no further integration methods are applied and 
the representation is computed directly from the AGE-corrected data, a 
different AGE correction approach may be preferred.

A potentially even more effective approach than removing genes 
with the highest AGE may be removing genes with the highest variation in 
AGE across batches (**Figure 3A**). However, this method may prioritize 
housekeeping genes, which are present in all cell types 
and thus their AGE is not determined by cell type 
proportions (**Figure 3B**). Unfortunately, housekeeping genes typically 
do not capture cell 
heterogeneity, defeating the primary focus of scRNA-seq analysis. 

![Desktop View](ambient_variation.jpg){: width="380" alt="Reducing ambient gene expression biases in cell representation by removing genes with the highest ambient expression differences across batches." .shadow style="border-radius: 7px;"}
_<b>Figure 3: Reducing ambient gene expression biases in cell representation by removing genes with the highest ambient expression differences across batches </b>(<b>A</b>). The limitation of this approach is that it will likely prioritize genes constantly expressed across all cells and subsequently batches (e.g. housekeeping genes). This can lead to the loss of information on biological variation (<b>B</b>)._

<details closed>
<summary><u>Note on removing AGE genes</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">
While using a custom method can seem like an unnecessary effort compared 
to established AGE correction tools, I nevertheless decided to select this 
approach for multiple reasons:
<ul>
<li>As noted earlier, the performance was comparable to that of established 
tools. Therefore, it seemed unnecessary to use more complex methods, 
whose limitations might also be harder to understand.</li> 
<li>Methods for AGE correction require parameter tuning (Janssen, 2023). 
The computational cost of filtering ambient genes based on a 
ranked list is lower than running correction tools multiple times. 
Ultimately, testing just two or three different numbers of blacklisted 
ambient genes sufficed for me.</li> 
</ul>
Furthemore, as I did not test the highest AGE variation approach, the 
above points are 
theoretical speculations that may or may not hold true in practice, 
likely depending on the specific implementation.  For example, in the top 
AGE removal approach, I observed that removing too few genes from the top of 
the AGE list did not result in adequate batch correction, while removing too 
many led to the loss of biological information.
</div>
</details> 

## Challenges of AGE correction for DE analysis

### <span style="color:#c96f00;">Effect of AGE on DE analysis</span>

In the scRNA-seq field, two common types of DE analysis are performed: 
within-batch and across-batch. They are differently affected by AGE effects 
and the biases of AGE correction approaches. 

The first type of DE aims to identify specific marker genes expressed highly 
in individual cell clusters. In this case, the same AGE effects are typically 
present across all compared cell populations, as data of individual batches is 
split up into clusters. Thus, for this type of DE analysis, it is primarily 
necessary that AGE correction is consistent between cell types within batches. 
Benchmarks have demonstrated that AGE correction can be beneficial in this 
context, as it reduces cross-cluster contamination from AGE (Janssen, 2023).

The second type of DE analysis is more complex, aiming to identify DE genes 
whose expression differs between groups of replicates (e.g. individuals or 
animals) with specific biological backgrounds (e.g. healthy or diseased). 
This type of DE analysis is crucial for answering key biological questions, 
such as identification of disease targets (i.e. genes changed in disease that 
could be targeted by therapy) and comparison of drug effects across 
populations (e.g. between males and females). However, each replicate 
typically originates from a different sequencing batch, resulting in unique 
AGE profile in each replicate. 

If AGE profiles contain group-specific biases, meaning they are more similar 
within than between replicate groups, this can lead to false positive genes in 
DE analysis (**Figure 4**). Such biases commonly arise due to both biological 
and technical factors. For example, in type 1 diabetes, beta cells are 
depleted compared to healthy pancreatic tissue. Consequently, sequencing 
type 1 diabetic pancreatic tissue will yield fewer exogenous transcripts 
from beta cells. Accordingly, if we performed a DE analysis on another type 
of pancreatic cells (e.g. alpha cells) between healthy and type 1 diabetic 
individuals, cells from healthy samples would exhibit higher gene counts for 
beta cell markers. These genes would be false positives caused by AGE.

![Desktop View](within_between_batch.jpg){: width="450" alt="Differential expression analysis between batches is more strongly impacted by ambient gene expression than within batches." .shadow style="border-radius: 7px;"}
_<b>Figure 4: Differential expression analysis between batches is more strongly impacted by ambient gene expression than within batches.</b> DE - differential expression._

### Limitations of AGE correction methods for cross-batch comparison

Current methods for AGE correction operate on a per-batch level. While this 
approach is theoretically sound, considering that AGE is a batch-specific 
artifact, in practice, this leads to different correction strengths across 
batches (Janssen, 2023). Such residual differences between batches can 
adversely impact DE analysis. 

The AGE correction methods aim to estimate the strength of AGE in each batch 
and use this to determine the contribution of AGE to the measured cell 
transcriptome, as described above. However, these estimates are never 
perfect (Janssen, 2023) (**Figure 5**). Indeed, I have observed that the 
expression of known exogenous genes after correction still varies among 
corresponding cell types across samples. For example, while insulin 
(an ambient gene originating from beta cells) was largely removed from 
alpha cells in some samples, it remained highly expressed in others. This 
discrepancy is even more pronounced when comparing samples with more 
substantial technical variation, such as across datasets from different 
laboratories.

![Desktop View](estimated_contamination.jpg){: width="400" alt="Estimates of ambient gene expression contamination often deviate from the actual levels and have different accuracy across batches." .shadow style="border-radius: 7px;"}
_<b>Figure 5: Estimates of AGE contamination often deviate from the actual levels and have different accuracy across batches.</b> Comparison of estimated AGE fraction obtained with different correction methods and the ground truth (genotype estimate). Different batches are shown on the x-axis, with boxplots showing the distribution of estimates across cells per batch. Batches originate from two different sequencing technologies, labeled as "rep" and "nuc". The plot was taken from Figure 5a of (Janssen, 2023), which is under CC BY 4.0 license._

As long as AGE correction differs across batches, I would not consider it 
sufficiently reliable for facilitating DE analysis across multiple batches. 
Evaluations of AGE correction methods have typically focused on within-sample 
tasks, such as identifying cell type markers and cell clustering 
(Janssen, 2023; Yang, 2020; Fleming, 2023; Young, 2020; Amezquita, 2021; 
Huang, 2024). The DE analysis using data from multiple batches was evaluated 
only rarely. Moreover, when such evaluations have been conducted, they have 
relied on a limited ground truth, based on only a few known positive or 
negative genes (Berg, 20203). However, this does not guarantee that most 
ambient genes are removed from the DE list.

For a while, I was playing with the thought of developing a new method to 
address this challenge. My primary idea was to jointly model endogenous 
expression components in similar cells across batches. This concept was 
inspired by current approaches that share endogenous expression information 
among similar cells within individual batches. Such a constraint could make 
the AGE correction more comparable across samples.

### Removing likely ambient genes from DE analysis

Depending on how detrimental false positives or negatives are in DE analysis, 
a more stringent approach to AGE mitigation may be necessary. For example, 
one of the aims of our DE analysis (Hrovatin, 2023) was to identify targets 
for laboratory validation, requiring higher reliability. Thus, I used an 
approach that retains only DEGs less likely to be AGE-driven false-positives.

As explained above, it is assumed that genes are relatively lowly expressed in 
cell types in which they are of ambient origin compared to cell types where 
they are endogenously expressed (**Figure 6A**). Thus, I decided to exclude 
DE hits with relatively low expression in the cell type on which DE was 
performed, as they could be AGE-artefacts. The relative expression can be 
calculated by scaling the expression from the cell type on which DE was 
performed, based on the cell type with the highest expression (Hrovatin, 2023), 
representing the endogenous expression levels, and empty droplets 
(Amezquita, 2021), representing the AGE levels. 

![Desktop View](relative_expr.jpg){: width="660" alt="Relatively low expression of a gene within a cell population can be indicative of ambient origin." .shadow style="border-radius: 7px;"}
_<b>Figure 6: Assessing if a gene may be of ambient origin within a cell population based on its relative expression.</b> Relative expression can be computed by comparing its expression to true ambient expression level in empty droplets and endogenous expression level in droplets with maximal expression (<b>A</b>). The maximal expression level may be underestimated if a too-coarse cell population resolution is used (<b>B</b>)._

Of course, this approach also has multiple limitations:
- It is prone to false negatives for endogenous genes with relatively low 
expression in the target cell type. However, unlike AGE correction applied 
early in the processing workflow, it allows for the correction strength to 
be tailored to the specific use case. 
- The cell clustering resolution used to determine expression levels in the 
scaling procedure will affect the outcome. For example, if only a small 
cluster of cells is endogenously expressing the gene, and the clustering 
resolution used for cell type annotation is too coarse, the final endogenous 
expression estimate will be underestimated (**Figure 6B**). Thus, I performed the 
calculations using a very high clustering resolution. 
- This approach does not evaluate whether the direction of AGE-driven DE 
aligns with that of the target cell type. An alternative method to address 
this is discussed in the next section.

### Excluding genes whose DE can be explained by ambient DE

To assess whether DE results within a cell type are driven by AGE, 
they can be compared to ambient DE from empty droplets 
(Amezquita, 2021). While the comparison could be done _post hoc_ on the DE 
results of both droplet types individually, a more statistically sound 
approach would incorporate the ambient levels directly within the DE design. 

To determine if the biological condition of interest explains DE beyond 
the differences in the AGE levels, a likelihood-ratio test (LRT) could be 
used. The LRT evaluates whether a generalized linear model (GLM) with 
the additional predictor variable of interest (full model) provides a 
better fit than a baseline GLM (reduced model) that only includes other 
predictor variables (i.e. covariates). 

To assess AGE-bias in DE, the following GLM-LRT design could be used 
(**Figure 7**):
- The outcome variable is the expression of a gene.
- The predictor variable of interest is the biological condition. 
This covariate is omitted from the baseline model.
- The baseline predictor variable is the AGE of the gene[^footnote3]. 

If the GLM model with added biological condition information does not improve 
upon the model that contains only the AGE factor, this suggests that variation 
in gene expression can be explained by AGE alone, with the condition factor 
not having a significant contribution. 

![Desktop View](lrt_design.jpg){: width="600" alt="Likelihood ratio test (LRT) for assessing whether differential expression is driven by the condition of interest or ambient gene expression." .shadow style="border-radius: 7px;"}
_<b>Figure 7: Assessing if differential expression is driven by the condition of interest or ambient gene expression effects using a likelihood ratio test.</b> G1, G2 - condition groups._

However, this approach again has some limitations:
- Custom gene-specific factors (i.e. AGE levels) are not easily used with common DE 
tools, such as edgeR and DESeq2. Namely, they need to be incorporated in 
the offset matrix. However, this matrix must also account for other effects, 
such as the number of reads sequenced for each droplet (i.e. library size) 
and optionally other gene-specific biases. This complicates the computation 
of the offset matrix and usually specialized tools are used to generate it. 
However, I am unaware of any tool that accounts for AGE biases in the 
offset matrix. 
- This approach may overlook genes with similar DE patterns across all cell 
types. In such cases, the AGE contribution of all cell types will be similar, 
rather than AGE being a mixture of diverse DE patterns from individual cell 
types. The latter usually leads to DE patterns not being a direct reflection 
of DE observed within any individual cell type. Thus, the DE of AGE will 
match the true DE of individual cell types, leading to insignificant LRT 
results.

## Key takeaways

Different data use cases call for different AGE mitigation approaches. 
Since most existing tools are primarily designed for within-batch 
applications, and current workarounds are often suboptimal, it would be 
great to have a tool designed specifically for removing AGE-biases in 
cross-batch DE analysis.

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
- Martin, B. K., et al. Optimized single-nucleus transcriptional profiling by 
combinatorial indexing. Nat Protoc (2023).

## Footnotes

[^footnote1]: As noted by Maren Büttner, ambient artifacts appear only in certain single-cell sequencing protocols, such as currently popular droplet-based technologies. However, use of other methods may in the future make ambient artifacts obsolete. An emerging example is sci-RNA-seq (Martin, 2022), which distinguishes individual cells based on multiple rounds of mixing small cell populations within wells and uniquely tagging them. Subsequently, all transcripts from a cell have a unique tag combination. The free-floating transcripts are not captured alongside individual cells but rather "mixed away”, thus they do not share tags with individual cells.

[^footnote2]: As the information captured by individual genes is redundant, cell representations are commonly computed on a subset of genes. Thus, genes that may contribute less to cross-batch differences can be prioritized. 

[^footnote3]: To be precise, AGE should be incorporated as an offset variable rather than a normal predictor variable. However, explaining this is beyond the scope of this post. See <a href="https://stats.stackexchange.com/questions/175349/in-a-poisson-model-what-is-the-difference-between-using-time-as-a-covariate-or" target="_blank">this discussion</a> for more information.
