---
title: "Not everything that can be counted counts"
date: 2026-11-15 00:01:00
last_modified_at: 2026-11-15 00:01:00
categories: [Machine learning]
tags: [benchmark, bioinformatics]  # TAG names should always be lowercase
description: The many facets of useful benchmarks.
media_subpath: /assets/img/2026-11-15-benchmarking/
image:
  path: dice.jpg
  alt: "<b>Devising meaningful Bio-ML benchmarks involves many different considerations.</b><br><i>This image is AI generated.</i>"
---

{% include toggle-details.html %}

A good benchmark is much more than a pipeline that combines methods, datasets, and metrics. At its core, it is a study of what actually matters to users.

Developing a robust benchmark can often be more challenging than developing a new method. - There are many aspects to consider, from potential metric biases to deciding what should actually be measured. These and other facets of benchmarking were discussed with 
<a href="https://suragnair.github.io/" target="_blank">Surag Nair</a>, 
<a href="https://www.helmholtz-munich.de/en/icb/malte-luecken" target="_blank">Malte Lücken</a>, 
<a href="https://konradkrawczyk.github.io/" target="_blank">Konrad Krawczyk</a>, 
<a href="https://www.linkedin.com/in/m-frank-erasmus-08370814/" target="_blank">M. Frank Erasmus</a>, and 
<a href="https://kdidi.netlify.app/" target="_blank">Kieran Didi</a>.

<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 15px 0px 15px 0px;">
<p>
<b>The discussion partners and their work</b>
</p>

<p>
Surag and his colleagues developed CompBioBench (Surag, 2026), a benchmark designed to evaluate agentic systems on realistic computational biology tasks. The tasks were carefully designed to capture different types of real-world challenges, including missing metadata and subtle tricks-of-the-trade.
</p>

<p>
Malte has designed several benchmarks and organised public competitions focusing on biological data analysis and modelling, particularly in single-cell omics (OpenProblems benchmark portal, Luecken, 2021; Luecken, 2025; Lance, 2026). Much of his work has focused on developing reliable evaluation strategies, analysing metric failure modes, and identifying properties that are not yet being measured (Lance, 2022). Building on these efforts, he also contributed to redefining best practices in single-cell analysis (Mueller, 2026).
</p>

<p>
Konrad has worked on curating protein structure data and benchmarking computational methods, including structure prediction and binder design. His understanding of the protein structure data, including experimental protocols and processing workflows, importantly influences his research.
</p>

<p>
Frank focuses on evaluating the utility of emerging machine learning approaches for developing antibody therapeutics. He co-organised a public competition, AIntibody (Erasmus, 2026), which assessed the usefulness of computational approaches across different antibody development tasks.
</p>

<p>
Kieran* and his colleagues developed FLIP2, a benchmark designed to investigate how well protein property prediction models perform across different biologically relevant tasks (Didi, 2026). To achieve this, they introduced different data-splitting scenarios that simulate a range of practical use cases.
</p>

<p>
* The discussion with Kieran was based on his FLIP2 paper, which he conducted during his studies at the University of Oxford.
</p>

</div>

*This post does not aim to provide a comprehensive overview of the field. Instead, it focuses on selected highlights from our conversations. It also does not represent the views of my current employer; its primary purpose is to share the perspectives of the domain experts I interviewed.*

*Although this blog post draws on discussions with Surag, Malte, Konrad, and Frank, I occasionally omit their names for the sake of readability.*

<details closed>
<summary><u>Sections list</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">
<ul>

<li>Benchmarks that earn their keep</li>
<ul>
<li>Evaluating the tool … or the craftsman?</li>
<li>Metrics are moody</li>
</ul>

<li>Two heads are better than one</li>

</ul>
</div>
</details>

## Benchmarks that earn their keep

“Today, we can build new tools quicker than ever before”, explained Malte, highlighting the potential of LLM-based coding agents. With recent advances, the process is getting close to being fully automated. The main question becomes: “Are these tools useful in practice?” The success of agentic coding has been driven in large part by unit test-based development, which provides immediate feedback on whether the code behaves as expected. However, this alone is not enough when developing bioinformatics methods. New tools must not only behave as expected (i.e., pass the tests), this behaviour should also be useful for biological applications. And defining what is actually useful in biology is an art in itself.

Building a useful benchmark involves much more than simply taking a handful of methods and computing RMSE on a few example datasets. Everyone agreed that a benchmark should reflect how methods are actually used in practice. Real-world scenarios are rarely simple enough to be captured by a single metric or represented by a single dataset. - In most cases, good performance comes down to balancing multiple factors.

One point that everyone highlighted was the importance of probing different failure modes. - While some limitations are relatively easy to anticipate, others are much less obvious. In fact, our intuition about how well a method performs can sometimes be misleading, as illustrated in the box below.

<details closed>
<summary><u>Failure is often unpredictable</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

<p>Letting the agent treasure-hunt for the data source - that was one of the most challenging tasks that the CompBioBench team came up with. They took a dataset and deliberately removed any information about the source paper. The agent then had to analyse the data, work out its biological context, and ultimately find the corresponding paper online. More specifically, the task involved gene expression data, which inherently contains clues about its biological context, including the tissue, organism, and treatment conditions (e.g., healthy or diseased). The agent had to carefully analyse these signals to piece together this information and identify the dataset's origin.</p>

<p>This was just one of the “challenging” ideas they had. Others included multi-step reasoning tasks and datasets with intentionally introduced experimental errors (e.g., incorrect metadata or mixed-up samples). To perform well in these scenarios, the agent needs to go beyond simply following instructions: it must actively explore and validate the data on its own. Going forward, there are many other challenging scenarios one could imagine. For example, instead of focusing on well-studied organisms such as humans or mice, benchmarks could include data from less well-studied species. This introduces several additional challenges, ranging from the scarcity of publicly available reference data (e.g., genome annotations) to generally more limited biological understanding.</p>

<p>However, what makes a task <i>challenging</i> for humans does not necessarily make it challenging for LLM agents. Surag, for example, observed that agents could master complex computational environment setups and optimize data downloads in ways that might take a human bioinformatician hours. Thus, exploring a wide variety of tasks could contribute to discovering unexpected failure modes, Surag noted.</p>

<p>Following the publication, newly developed coding agents have already saturated the benchmark, as the live leaderboard shows. However, Surag remains unsure whether this level of accuracy would carry over to larger projects with more subtle <i>traps</i>.</p>

</div>
</details>
<p></p>

What are the tasks that actually matter for practitioners using the method? - This is a question that should not be overlooked, although it often is in practice. Kieran explained that protein optimization is performed in many different ways. The key, therefore, is to simulate the different scenarios in which models are expected to generalise. Examples include predicting the effects of mutations at previously unseen sequence positions[^footnote1], capturing interactions between mutations (i.e., epistasis)[^footnote1], and working with realistic (relatively small) dataset sizes[^footnote2]. In their benchmark, they observed substantial variation variability in performance across these scenarios. Given the many edge cases that inevitably arise in practice, it is worthwhile thinking far beyond the most canonical task definitions.

<details closed>
<summary><u>What else matters in protein design?</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

<p>Konrad and Frank also highlighted several other evaluation aspects they would like to see explored in future benchmarks. For example, Konrad suggested benchmarking de novo design across a range of targets with varying levels of structural confidence, as targets with poor structural information are known to pose greater challenges for de novo design. Frank, meanwhile, suggested evaluating binder design against target classes that are not yet widely used in clinic (e.g., G protein-coupled receptors and ion channels), as there is generally less publicly available information about their biochemistry and existing binders. Besides the lack of data, these targets also involve a genuinely different biochemistry, which poses challenges for experimentalists and could likewise do so for computational tools.</p>

<p>Furthermore, evaluation should be focused on parts of data that count the most. Konrad illustrated this with the example of using RMSE to measure the difference between true and predicted protein structures. While the metric itself is straightforward, deciding how to apply it to protein data is not. For example, when working with antibodies, it is relatively easy to predict the framework regions (FR), which are relatively constant and comprise the largest part of the molecule. However, the more interesting question is how well a model predicts the complementarity-determining regions (CDR), which are exceptionally variable while being key for binding. As a result, most models these days are close to perfect predictors of the ‘overall antibody fold’. Yet, the small part they still often get wrong can make them practically useless for many real-world applications.</p>

</div>
</details>
<p></p>

Moreover, what constitutes a useful task can differ substantially across communities. One may think of binder design primarily in terms of the affinity achieved. However, as Konrad and Frank explained, the bar for a successful therapeutic molecule is much higher, including efficacy *in vivo*, off-target effects, and safety. Getting the full picture of relevant properties can be challenging, Frank noted. For example, during their competition, they overlooked a key property that would have disqualified a molecule in a real drug development campaign. As a result, the *official* competition winner was not actually a viable candidate for practical applications.

In fact, while many benchmarks focus on pre-clinical properties (e.g., binding to the target and off-target), the main headache for therapeutic development is actually clinical translation. However, the properties that can be measured in the lab often fail to translate into the success of clinical trials in real patients. Thus, solving the “binding” problem is a long way from tackling the most pressing challenges in drug development.

<details closed>
<summary><u>Construction of valuable benchmarks often falls short at the data collection stage</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

<p>Finding the right data is at the heart of building realistic and diverse benchmarking scenarios. However, Konrad and Kieran explained that biological data is often generated to support a specific paper or patent, rather than with method development in mind. One prominent example, highlighted by Frank, is the bias towards positive data. Laboratory methods are often designed specifically to identify molecules that perform well. Surface display technologies, for instance, sift through a vast pool of proteins to enrich them for binders. Non-binders are typically discarded, while only the binder subset is characterised further. Thus, benchmark questions that involve non-binders are harder to assess.</p>

<p>Similarly, Kieran raised concerns about gaps in the available data that, if addressed, could change how we approach protein optimisation. Currently, development efforts tend to focus on finding a single good candidate, disregarding other parts of the protein sequence landscape that could likewise lead to good performance. Developing methods that can identify multiple peaks in this landscape and efficiently navigate between them will likely require dedicated data generation. Kieran was also enthusiastic about lab-in-the-loop approaches, where models actively inform subsequent data collection. He noted that although iterative approaches are already common in industry, they have not gained sufficient traction in academia.</p>

</div>
</details>
<p></p>

Beyond relevant tasks, every benchmark also needs meaningful baselines. These are often implemented as relatively simple methods (e.g., linear regression). However, baselines should serve a broader purpose: helping us understand whether differences between methods are practically meaningful and whether the best-performing method is actually good enough. For example, when it comes to computational protein design, the baseline should really be the standard laboratory discovery approaches. Frank explained that it is not only the computational methods that are advancing rapidly. While a certain laboratory step may have taken a few months in the past, many timelines have shrunk to a few weeks, reducing the edge of de-novo design. Thus, while he is excited about the advances that AI could bring to biology, the results of their competition[^footnote3] did not yet make a particularly compelling case for its practical utility.

<details closed>
<summary><u>Good performance is not enough to bring the field forward</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

<p>Performance is not the only thing that matters, Malte explained. In their Kaggle competition, many participants achieved good results simply by trying out lots of different things and stacking together a collection of solutions*. This makes it difficult to understand exactly what enabled the top-performing methods to outperform the others – a common issue in public competitions, as both Malte and Frank pointed out. To disentangle the contributions of individual components, Malte's team conducted ablation sweeps. This helped them identify which components were actually responsible for good performance and may be promising for future method development.</p>

<p>Malte also advocated for greater scrutiny in public competitions (e.g., Kaggle). - Ideally, a submission should only be eligible to win if its approach can be independently re-implemented.</p>

<p>* One might expect methods that have been heavily optimised for a specific benchmark to be brittle, breaking down when usage conditions change even slightly. However, this was not the case in this competition: the top-performing methods also performed on a par with state-of-the-art (SOTA) methods in an independent evaluation. Malte explained that well-designed benchmarks, which capture the complexity of real-world applications, can help mitigate the brittleness introduced by benchmaxing. That said, the risk of over-optimisation can never be entirely eliminated.</p>

</div>
</details>
<p></p>

### Evaluating the tool … or the craftsman?

"Benchmarks often measure the proficiency of competing teams rather than the quality of the method" Konrad said with concern. “And measuring how well the developers perform is not particularly useful – we already know they are experts. Instead, we should focus on how well the method performs in the hands of an average user.” - Konrad and Frank outlined examples where performance stemmed from prior experience, as described in the box below.

One factor that gives experts an important advantage is that any biological data is merely a proxy and not the ground truth. “The computational models we build on top do not model physical truth but rather the experimental effect”, Konrad pointed out. Even when working with well-established resources such as the PDB, the data still need to be postprocessed to provide a reasonable representation of biology. He gave the example of SAbDab, a prominent antibody structure database. When they first published it, the publicly released version was already version 3 of their internal resource: a lot of things had needed fixing to produce high-quality data. He added that even after having worked in the field for 15 years, he is finding - and sometimes overlooking - unexpected quirks in the data. - And he doubts this would change after another 15 years of experience.

<details closed>
<summary><u>When does experience count - and when not</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

<p>Konrad and Frank both emphasised how much success in protein design campaigns depends on domain expertise. In the AIntibody competition, the success was often tied to teams actively working in the field - not just on the method development side, but in the lab as well.</p>

<p>For example, Aureka, the winner of the affinity maturation challenge*, has experience and proprietary data in this field. It was also surprising to see that the ProBioGen team, who has experience in wet-lab antibody development, performed competitively with a very simple statistical approach. Similarly, the UCSD team, which did well in the challenge on identifying high-affinity antibodies*, had extensive experience with the laboratory method used to generate the input data provided to the teams.</p>

<p>In an ideal world one could encapsulate all this knowledge in a model. However, Konrad was not convinced that this would currently match the performance of an experienced team.</p>

<p>That said, domain expertise is not always the deciding factor. Malte pointed out that, in their competitions, many teams performed competitively despite having no background in single-cell biology. A few things may have helped level the playing field for newcomers: the data had already been pre-processed by domain experts, and the tasks resembled more familiar machine learning problems, such as prediction or translation.</p>

<p>* The goal was to improve the affinity of an existing antibody (i.e., the binder). Participants were given a parental antibody, along with examples of improved variants obtained through laboratory screening (yeast display). However, the affinity measurements for these examples were not provided.</p>

<p>* A pool of antibodies with varying affinities was generated through laboratory screening (yeast display). The teams were given this pool and asked to identify the antibodies with the highest affinity.</p>

</div>
</details>
<p></p>

The same craftsmanship bias applies to benchmark design. - To design high-quality benchmarks, the authors should seek expertise in both the evaluated methods and the data. - Which goes beyond understanding the key use-cases in the field. When asked what he would do differently if he were starting the project again, Kieran's first thought was that he would engage with the data authors much earlier. Understanding the limitations of each dataset, as well as what it can offer, is essential for using it meaningfully in a benchmark, as described in the box below. Malte made a similar point about methods: without consulting their authors, it is all too easy to make mistakes when applying them.

<details closed>
<summary><u>Are all numbers quantitative?</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

<p>Kieran explained that numerical measurements cannot always be taken at face value. Experiments are often designed to identify the best candidates. As a result, the signal-to-noise ratio can be very low at the lower end of the measurement range: there is little practical reason to tell a poor candidate from an even worse one. In such cases, numerical values may be better understood as ordered bins rather than precise measurements, with the boundaries between these bins depending heavily on the experiment.</p>

<p>These considerations also have implications for how we evaluate predictive performance. For example, measuring correlation within individual bins (e.g. good, mediocre, and bad candidates) may not be particularly meaningful if the values are dominated by noise. Instead, Kieran highlighted that using top-enrichment metrics (i.e., identifying best candidates) is more valuable. Another complication is that datasets differ in their noise levels, and therefore in the upper limit of the performance that can realistically be achieved—even with bounded metrics such as correlation. Malte therefore emphasised the importance of including both positive and negative baseline methods. These help calibrate the metric boundaries to reflect the <i>effective</i> range of performance, rather than the theoretical one.</p>

</div>
</details>
<p></p>

During benchmark construction, many apparent agent errors ultimately turned out to be human errors in task design, Surag explained. These included underspecified problems or unexpected issues with the input data. To avoid this, they put their tasks through extensive review by a group of experts, making sure that underspecification could not lead to ambiguity in the expected answers. A task that should take an agent two hours to solve could itself take twice as long in human-driven development. This included trying to solve the task themselves and testing it with an agent. As Surag put it, these days, when an agent gets something wrong, the first thing worth checking is whether you gave it the right context.

### Metrics are moody

The idea that “all models are wrong, but some are useful” applies to metrics, too. Malte’s ideal benchmark would not start with method evaluation - but rather metric evaluation. He emphasized the importance of testing metrics in different scenarios - both under different data and methodological properties - to uncover the biases and limitations that every metric inevitably has (Mueller, 2026; Lütge, 2021). He explained that even carefully designed public competitions, including their own[^footnote4], often have evaluation issues. This also motivated him to devise “living” benchmarks, which are described in the section below.

Simple metrics are easier to understand and make it easier to draw actionable conclusions from - however, this does not guarantee their quality. Malte shared examples where their initial intuition about which metric to use turned out to be wrong, and a less intuitive, harder-to-understand alternative proved more appropriate. Similarly, Konrad pointed out that even when a metric looks simple on paper, the biological reality it needs to capture rarely is, as discussed above.

While metrics need to account for the characteristics of a domain, they should not be biased towards it. For example, many evaluations of LLM agents rely on rubrics[^footnote5], but Surag deliberately chose not to use them. “Rubrics may bias the evaluation towards human expectations”, he explained. “But there are often many ways to solve a bioinformatics problem. - And agents may choose approaches that humans would usually not consider.” Instead, they designed each task to have a single correct answer, while leaving room for different approaches to reach it - as long as the chosen bioinformatics approach is suitable.

In the context of LLM agents, Surag emphasised that human intuition about task difficulty should not be taken for granted. For the CompBioBench dataset treasure hunt task (described above), they initially removed sample identifiers and metadata from the data, expecting this would create a challenging source-identification task. However, all their test runs finished quickly - and returned the correct answer. When they inspected the agents' approach, they discovered that the raw data contained two custom transcripts[^footnote6] that gave away the source. No human would typically start an analysis by combing through tens of thousands of transcript names, but for the agents, this turned out to be an easy win.

Another important consideration is the choice of *ground truth*. As discussed above, biological measurements are far from being the *ground truth* themselves. The simplest approach is to ignore this distinction and treat the measurements as the ground truth for a task - that is, directly predicting the measurements. However, this can fall short when the aim is to design new molecules that must pass downstream laboratory validation.

When laboratory validation is involved, we cannot ignore that the measurements are biased and noisy. Frank and Konrad emphasised the importance of repeating laboratory validation across different testing providers. They also expressed a wish for greater consistency between results reported by different laboratories. - Since experiments are performed by different laboratories, the results cannot be compared one to one, as is common practice in standard machine learning benchmarks.

## Two heads are better than one

Benchmarks should be considered as living projects rather than one-off publications, Malte explained with Open Problems in mind. This makes it possible to update them as limitations are discovered or when new methods and metrics evolve. Moreover, the long-lived nature also makes it easier to incorporate community feedback, which is essential in defining useful benchmarks.

Malte shared several examples of how community engagement helped improve OpenProblems, sometimes in ways they had not anticipated. For example, they made special effort to enable benchmarking of not only Python-based methods, in which their benchmarking framework has been based, but also R methods through Python wrappers. “We were convinced that this was a good solution”, Malte recalled. But feedback from the R community soon revealed a different perspective: “R users felt like second-class citizens” in their framework. Writing Python wrappers around R methods was cumbersome and made the benchmarking process slower. For the next version, they therefore decided to adopt Viash, which streamlines script execution regardless of the programming language used.

A second example was their 2022 Kaggle competition on multimodal single-cell integration[^footnote7]. The benchmark results were far from the only valuable outcome. - Just as important was the feedback they received on both the submitted methods and the benchmark setup itself. This feedback had a significant influence on how they interpreted the results and shaped their future benchmarking efforts. To recognise this contribution, they introduced a separate prize for the best benchmark commentary. “We are still in contact with many of the participants,” Malte noted at the end, highlighting how these new connections went on to contribute to their future projects.

<details closed>
<summary><u>Finding the right platform</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

<p>Malte explained that hosting the competition on Kaggle, with its large and diverse user base, was key to attracting community engagement. They had organised a similar competition before, but received much less input from the community, partly because they had chosen a more niche platform.</p>

<p>However, while community engagement brings clear benefits, it is also difficult to sustain. Malte explained that they continuously invest effort in keeping the community active, particularly as original contributors move on. In-person events, such as hackathons and method jamborees, play an important role in keeping the community alive.</p>

<p>Last but not least, bioinformatics methods often involve multiple, often disjoint, communities. As Malte explained, Kaggle was a great way to reach machine learning practitioners. But to build benchmarks that are genuinely useful to the people using these methods, it is equally important to engage the bioinformatics and broader biology communities.</p>

</div>
</details>
<p></p>

Benchmarks organised by a broader community, rather than a single group, can also help build trust. The AIntibody organisers had expected many of the prominent *de novo* design groups to take part, but this did not happen. “Much of the feedback we received reflected concerns about a commercial entity (Specifica) leading the competition”, Frank lamented. For the next iteration, they therefore handed over the competition to a non-profit consortium.

## Key takeaways

While the speed of method development is increasing, benchmarking is only going to become more important. The scientific community will therefore need to keep discussing what good performance actually means and how best to measure it in a meaningful way.

## References

- Didi, et al. FLIP2: Expanding Protein Fitness Landscape Benchmarks for Real-World Machine Learning Applications. ICML (2026).
- Erasmus, et al. A blinded, prospective benchmark of in silico antibody discovery anchored to experimental affinity and developability. Nature Biotechnology (2026).
- Lance, et al. Multimodal single cell data integration challenge: Results and lessons learned. PMLR (2022).
- Lance, et al. Longitudinal modality prediction learns gene regulatory patterns: insights from a single-cell competition. bioRxiv (2026).
- Luecken, et al. Benchmarking atlas-level data integration in single-cell genomics. Nature Methods (2021).
- Luecken, et al. Defining and benchmarking open problems in single-cell analysis. Nature Biotechnology (2025).
- Lütge, et al. CellMixS: quantifying and visualizing batch effects in single-cell RNA-seq data. Life Science Alliance (2021).
- Mueller, et al. Building optimized single-cell reference atlases with scAtlasTb. bioRxiv (2026).
- Nair, et al. Agentic systems are adept at solving well-scoped, verifiable problems in computational biology. bioRxiv (2026).

## Footnotes

[^footnote1]: For the task of predicting mutations (i.e. changes) at new positions, the training data included protein sequences (i.e. samples) with mutations at certain positions, while the test data contained mutations at positions that had remained unchanged (i.e. retained their original values) during training. For the interaction task, the training data included sequences with mutations at individual positions, while the test data contained sequences with pairs of mutations.
[^footnote2]: One thing that is often overlooked in protein optimisation is how much data is actually generated during laboratory campaigns. While many benchmarks use thousands of protein samples (i.e. mutants) for training, most campaigns stop after generating just a few dozen or a few hundred.
[^footnote3]: It is worth noting that they had deliberately chosen an easy target, for which plenty of public data was available.
[^footnote4]: In one of their competitions, they used per-sample preprocessing that resulted in different scales across samples. Combined with a metric that measured absolute errors (RMSE), this meant that the winners were those who managed to decode the per-sample scaling factors rather than capture the underlying biology (Lance, 2022).
[^footnote5]: Rubric evaluation uses an LLM judge to assess the outputs of an LLM agent. The judge is given a predefined rubric outlining what to evaluate (e.g. solution correctness, methodological robustness, etc.), along with positive and negative examples to guide its assessment.
[^footnote6]: The authors had genetically engineered the cells to introduce additional genes. The transcripts of these genes appeared under custom names in the scRNA-seq count matrix, and these same names also appeared in the paper, providing a clue that linked the dataset to its source publication.
[^footnote7]: Multi-modal single-cell integration aims to align representations of datasets that share a biological origin (e.g. the same tissue) but measure different aspects of cellular biology (e.g., gene expression or regulation thereof).
