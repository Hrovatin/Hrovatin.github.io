---
title: "Steering through the clinical trial landscape"
date: 2026-07-07 00:01:00
last_modified_at: 2026-07-07 00:01:00
categories: [Machine learning]
tags: [clinical trials, data curation, predictive modelling]  # TAG names should always be lowercase
description: Good model performance is only one of many steps towards clinical trial adoption.
media_subpath: /assets/img/2026-07-07-clinical_trials/
image:
  path: robot.jpg
  alt: <b>Developing new approaches that are ultimately adopted in clinical trials can feel like a wrestling through the thicket.</b><br><i>This image is AI generated.</i>
math: true
---

{% include toggle-details.html %}

Good predictive performance alone won't get new methods into clinical trials. A major roadblock that needs to be bypassed is finding a place where they add value.

New computational methods are pushing the boundaries of what is possible. - However, many obstacles remain: hard-to-access data, strict quality and interpretability requirements, and rigid trial processes. We discussed how to overcome them with <a href="https://www.linkedin.com/in/raulrodriguezesteban/?originalSubdomain=ch" target="_blank">Raul Rodriguez-Esteban</a> (Roche), <a href="https://www.linkedin.com/in/jpetrochuk/" target="_blank">Jessica Petrochuk</a> and <a href="https://www.linkedin.com/in/adirshaham/?originalSubdomain=il" target="_blank">Adir Shaham</a> (PhaseV), and <a href="https://www.linkedin.com/in/simon-romanski/" target="_blank">Simon Romanski</a> (Atlas Bio).

*This post does not aim to provide a comprehensive overview of the field; instead, it focuses on highlights from our conversations.*

*While this blog post is based on discussions with Raul, Jessica, Adir, and Simon, I often omit their names for the sake of readability.*

## Brief technology background

### Raul’s methods for unstructured data

Raul is exploring strategies for improving drug development by extracting information from unstructured sources at Roche. This includes both real-world data, such as social media posts from patients and health records accumulated through individuals’ lives, as well as more narrowly defined data from clinical trials[^footnote1].

Through our conversation, he stressed the importance of selecting the right tool and approach for each individual use-case, rather than following the general technology hype. For example, he pointed out that while large language models are great for extracting information from messy real-world data, older NLP approaches (e.g., text embeddings) are still important for information retrieval. 

### PhaseV’s collection of tools & data

<a href="https://www.phasevtrials.com/" target="_blank">PhaseV</a> is building a comprehensive platform for clinical trial optimization and analysis. It offers interactive tools, data management systems, and algorithms that support trial design, clinical operations, and patient stratification. Adir explained that through numerous use-cases, they have built a diverse palette of tools for different questions. For him, the most fun part of any new use-case is opening this toolbox and selecting the best tools for the task at hand.

In our discussion we primarily focused on different aspects of data curation, with Jessica having passionately explained current limitations and ways forward. Data is one of PhaseV’s cornerstones, being important both in developing new prediction tools as well as in providing users with meaningful analysis interfaces. - Without thoroughly understanding the data space, PhaseV would not have been able to understand the user's needs.

### Atlas Bio’s model

<a href="https://atlas.bio/" target="_blank">Atlas Bio</a> aims to predict how the whole cellular metabolism (i.e., gene expression, also called transcriptome) changes based on the drug's mode of action - that is, perturbation of specific parts of metabolism targeted by the drug. With Simon, we had a detailed discussion around both how the model was developed as well as how it may change the assessment of drugs’ potential in the future.

Models for predicting drug effects are usually conditioned on patient metadata (e.g., sex, age, etc.). In contrast, Atlas Bio's model is designed such that drug-patient interactions do not need to be learned from small clinical datasets. Instead, their model learns general covariance patterns between human genes. - That is, the model is primarily pre-trained on diverse human datasets[^footnote2]. Specifically, during pre-training they mask the majority of the transcriptome and aim to reconstruct it from a few “observed” genes. At inference time, the effect of a drug on the transcriptome is predicted as effects that propagate from the drug's target genes (selected based on mechanism of action, MOA) to the rest of the transcriptome (**Figure 1**). To make this possible, they designed a model architecture that is sensitive to changes in a small number of genes rather than disregarding them as noise. 

![Desktop View](atlasbio_schematic.jpg){: width="470" alt="Schematic of Atlas Bio’s model." .shadow style="border-radius: 7px;"}
_<b>Figure 1: Schematic of Atlas Bio’s model.</b> The model is analogous to image inpainting. If the sparse pixel input is perturbed (e.g., by adding a dog silhouette), the model will predict a slightly different illustration. - It understands that the dog will scare away the ducks, inpainting less of them on the perturbed image. Similarly, Atlas Bio’s model is trained to restore gene expression of all genes from a small subset of genes (bottom left). During the inference (bottom right), MOA is applied to the input subset of a new patient. As the restoration is based on a perturbed input, it becomes a prediction of treatment effects._

This metabolism-wide rather than covariate-based focus increases inference flexibility:
- Any MOA can be applied to the target patient sample. Thus, the model can predict effects of arbitrary drugs (i.e., MOAs) on diverse diseases (i.e., the patient samples used as inference input).
- Their model does not predict disease status (e.g., healthy/diseased or disease grade), but rather the whole transcriptome. Thus, they can answer arbitrary questions about the response, ranging from disease regression to the onset of side effects.
- To predict effects of specific clinical trials, the perturbation prediction is done on patients that match the clinical trial inclusion criteria[^footnote3]. With this, Atlas Bio answers the question of how the drug affects the target population. For example, it may affect young people differently than old as their baseline transcriptome differs. 
- Perturbation is applied on a per-patient level, which can reveal response outliers. Namely, patients within the target population may differ from each other, often by “unknown” factors. It may be impossible to model such effects as metadata-drug interactions, since the metadata for specific patient descriptors (e.g., clinical measurement) may simply not be available. However, the effects may still be deduced from the transcriptomic changes given that the transcriptome comprehensively describes the full patient state.

## How is ML changing clinical trials?

When you are pitching a startup, VCs will ask for a long‑term vision: if your idea succeeds, what does the future look like? Right now, clinical failure is the biggest bottleneck for drug development. Higher predictability of clinical success would thus enable many more organizations to develop drugs. If trials were more likely to succeed, companies would not need to “spread the bets” across many programs to guarantee that at least one wins - which is one reason[^footnote4] why trials are conducted by larger companies who can finance multiple concurrent trials. That shift would allow smaller teams to carry drugs from discovery through approval. 


<details closed>
<summary><u>How large is the therapy market, really?</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

Better predictions of drug success would raise development throughput, but it is unclear whether the market could absorb all those therapies. Simon speculated that demand would most readily materialize for therapeutics that people would be prepared to pay for from their own pocket, such as therapeutics against life-threatening conditions (e.g., cancer) or vanity drugs (e.g., weight-loss).

</div>
</details>
<p></p>
<p></p>

Looking at current trial practices, one may expect for clinical trial prediction to be most useful during trial planning. - That is, pharmaceutical companies could computationally screen drug performance across different diseases and patient populations before committing to a specific trial. For example, they could identify the patient population with the strongest effect or choose the indication that gives the best chance to be first to market. 

However, Simon noted that current incentive structures make it less likely for clinical trial managers to do this. Often, clinical teams come in contact with external drug success prediction tools too late, with a lot of resources already having been devoted towards designing the trial. Thus, they are less inclined to review their plans based on advice from small startups that only recently entered the field. 

Raul noted that researchers inside companies face similar issues. Clinical trials are heavily regulated, so changing a trial midstream - after the plan has been approved - is difficult[^footnote5]. 

Instead, Simon highlighted a few areas where their model drew more interest for immediate use:
- Post phase II failure assessment: following phase II failures, there is often interest in evaluating the mechanism of action (MOA) for alternative indications. He remarked, wryly, that luckily for them, 70% of phase II trials fail. 
- Indication expansion: therapeutics often first receive approval for rare genetic disorders with strong clinical need and well‑characterized disease mechanisms. However, the same drug could be later expanded to other diseases. 
- Increasing in-licensing success via enhanced reproducibility of early trials. A drug developed in one ethnic group may not translate to another group on which the buyer plans to apply it. Simon gave anifrolumab as an example - initial phase III trials failed, but the drug was later approved for a subpopulation with a high interferon signature, a trait linked to Asian ancestry.

Raul also explained that supporting a trial at the planning phase could potentially allow the use of new approaches. However, new approaches often lack guarantees to perform well on any arbitrary new dataset, limiting adoption. Furthermore, being involved in a trial from start to end is a long process, taking a few years from planning to execution and outcome.

<details closed>
<summary><u>Why is computational clinical trial modeling not a more popular research topic?</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

Data scarcity often gets the blame, but there are deeper reasons the trial space has not caught on with the ML community. Simon suggested long timescales are a key limitation - researchers prefer quick tests over waiting years for trial results. On top of that, Raul noted that it is harder to publish research results related to clinical trials because the publishing of associated information is under strict supervision. Trial sponsors (i.e., pharmaceutical companies) must namely ensure that shared information meets ethical standards and does not spread misinformation about the therapy, which could confuse stakeholders (e.g., doctors and patients).

</div>
</details>
<p></p>
<p></p>

Broadly speaking, PhaseV also pursues the goal of computationally testing different hypotheses during trial design. However, Adir explained that we are still far from certainty when it comes to clinical trials: While trials are planned based on rigorous science, there is always a level of uncertainty that must be surmounted by expert judgement. PhaseV’s tools help experts weigh different hypotheses by estimating their probabilities and interpreting the existing clinical evidence. 

Jessica and Adir also emphasized that tools must be flexible enough to support diverse priorities:
- Different applications demand different tradeoffs between predictive performance and interpretability. For example, patient-level effects (e.g., drug response) usually require mechanistic explainability to understand why a drug works or not. On the other hand, operational planning questions (e.g., predicting recruitment timelines) require a different balance between explainability and predictive performance. While transparency into the key drivers remains important, the ultimate value comes from forecasts that are reliable enough to support planning and execution.
- In some trials it is more important to optimize cost, while in others there is a tight race for being the first on the market, requiring timeline optimization.
- Every trial includes diverse partners, such as operation leads and clinicians who bring different interests and expertise. Jessica highlighted that giving interactive access to non‑technical users helps democratize trial analysis.

Moreover, patient data should not be evaluated only during trials. - Raul stressed that collecting information on what patients actually struggle with (e.g., from social media) could transform drug development. Rather than starting from disease‑target identification, we should first learn patients’ biggest challenges. For example, side effects may discourage patients from taking a drug designed for their disease. 

## Building new clinical trial tools

The number of new ML methods for clinical trials is growing fast. Raul remembers a pre‑AI era when many avenues were still unexplored; now it feels like no rock is left unturned.

Even so, the ML method field is still far from having transformed clinical trials practice. The above described rigid clinical trial practices are by far not the only culprit. Rigid trial routines are not the only problem - development is often held back by scarce data and concerns about method reliability slow down adoption.

### How to evaluate new methods?

Real-world validation of clinical trial prediction methods can be complicated for startups and academics as trial data is inaccessible. Usually, only trial descriptions and outcome summaries are available while raw individual-level measurements remain unpublished. Raul noted that even employees at sponsor companies who are not on the trial team may lack access to this data. 

Luckily for Atlas Bio, their approach requires only publicly accessible data (i.e., MOA, patient inclusion criteria, and outcome information)[^footnote6]. Thus, Simon believes that being a startup actually widens their validation options. - They can test the method on trials from different companies. Crucially, this enables them to fully validate their method on their own, without relying on partnerships for real-world testing.

Nevertheless, Simon warned about common self‑deceptions that make a model seem better than it is:
- When modelling treatment effects most genes will remain unchanged. That is expected, as drugs are designed to have a specific target with minimal effect on the rest of the cell metabolism. However, this means that it is easy to score well on the majority of genes. For that reason, their validations focus on genes that are either expected to change in real treated data or that change in the model’s predictions.
- Looking at benchmarking numbers is not enough. During late-stage evaluation, one of their bioinformatics scientists analyses and interprets the predicted dataset as if drawing trial‑critical conclusions. For example, if some genes change, what would that mean for a patient's health? Is the treatment effect large enough relative to the standard of care (i.e., the standard therapy), or are predicted side effects too big to ignore?
- Too early validation on real use-cases, when the model is still under development, will inevitably lead to overfit to the test set trials. To avoid this, they run multi‑stage validations: during development they iteratively check general reconstruction performance, and reserve real trial predictions for the end.

<details closed>
<summary><u>Assessing the model on the hardest parts of cellular metabolism</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

There were a few challenging prediction settings where Simon was happy to see that their model still performed well enough:
<ul>
<li>Most of their data comes from blood samples. However, treatment-relevant effects require prediction on different tissues, some of which are scarce in their training data (e.g., lung tissue).</li>
<li>Lowly expressed genes are hard to model, as they are often missing from the data (i.e., the signal is too low to be measured). Still, these genes matter: many are key regulators of cellular metabolism (e.g., transcription factors).</li>
</ul>

</div>
</details>
<p></p>
<p></p>

The validation, about which they were most excited, was a prospective study. - They published their prediction of a trial outcome before the results were known. Simon said he wishes they had started doing prospective validation earlier as it is the strongest proof for good performance. 

<details closed>
<summary><u>Are humans really harder to predict than mice?</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">

They were surprised the model performed well not only on mouse data but also on human data. Human datasets are regarded as more challenging due to diversity in lifestyles and genetics compared to mice, which are bred and raised in controlled conditions. One possible explanation as to why their model works well on human data is that they do not model patient covariate effects (e.g., sex, age, etc.). With a very diverse population, predicting how a patient with specific covariates would respond is difficult: many covariates are unknown, some lack enough data to learn covariate-outcome links, and there are too many covariate combinations to capture interactions. However, since they only model relationships between genes, and not genes and covariates, it is easier to make predictions for a new population (e.g., different ethnicity). The set of genes is the same across humans, and gene interactions can be learned efficiently from sources that capture metabolic diversity (e.g., public human samples).

</div>
</details>
<p></p>
<p></p>

Overall, discussions with Simon and Raul revealed that validation is as complex as model building and deserves the same level of attention. Thus, keeping the scope small at the beginning and focusing on a single disease area (e.g., autoimmune, oncology) can be beneficial. - For practical use, it is better to demonstrate the model works sufficiently well in one area than to collect evidence indicating it might be applicable across diseases.

#### Benchmarking against expert intuition

At the end of the day, it’s not enough to show a model predicts biology - it must add value beyond effects experts can anticipate. Simon explained that key opinion leaders understand disease metabolism and can thus anticipate some drug effects. That may be sufficient in new disease areas, where any therapy is welcome, but not in crowded fields like immunotherapy, where small differences decide which drug succeeds. There, more nuanced prediction of treatment effects is needed. For instance, choosing between a target inhibitor or a degrader is a decision where human judgment can fall short - a reason they first focused on autoimmune diseases, where many therapies compete.

Similarly, the prediction of complex biological interactions between different metabolic pathways and cell types is challenging for human intuition. For example, immune processes often involve multiple cell types that communicate and act on each other. A recent example is treatment of ulcerative colitis, where a certain class of immune T cells was believed to drive inflammation. However, a therapy targeting them failed to improve the disease while broader anti‑inflammatory treatment did. That suggests other, unknown immune factors are contributing to the pathology. Simon was thus happy to see that their model predicted that depleting this T cell population would not suffice.

### A lion’s share of work goes to data collection

Meaningful conclusions start with understanding the data. Jessica and Adir emphasized that even when a path to the goal looks straight, real data will inevitably complicate it. As one gets to understand the data and the stakeholder needs better, the initial plan will change. - For Jessica, assembling those messy puzzle pieces to reveal a clear picture of the trial is the most rewarding part. 

At the end of the day, teams must move from data preprocessing to building the tools and models that are their main product. Adir and Jessica highlighted the hardest part is balancing necessary data exploration with processing speed. - However, it seems that data curation is an uphill slog for everyone. Simon also mentioned that across model training, evaluation, and data collection, the latter consumed 40% of their time.

#### Is there ever enough data?

Access to relevant data is often limited, Raul noted. Complicated data sharing policies block sharing with collaborators from other institutions. He noted that industry‑academia partnerships work best when the academic (e.g. PhD student) is directly employed by the company, significantly easing access to company-internal data. That said, data scarcity is often also a consequence of insufficient data acquisition strategies at the company level. He also argued that the value of textual data is often underestimated, missing useful information from publications, electronic health records, and patents.

Another important thing to keep in mind is that not all data is created equal. At Atlas Bio they only kept datasets they were confident will help their goal, that is modelling real human biology. Several data properties had to be considered:
- Relevant biology: In Atlas Bio they decided against cell line data because it diverges from human metabolism. Similarly, Adir warned that historical data may not always reflect the current standard of care. In many areas the standard is changing rapidly (e.g., oncology, obesity, COVID), meaning that data is quickly outdated and thus a poor control proxy for new therapies. 
- Assays that capture relevant biology: While single-cell data has overcome bulk data in popularity[^footnote7], bulk data still has some benefits, Simon explained. It better captures cell type proportions, which matter for modeling tissue-level effects, such as cell-cell interactions. 
- Minimize technical artefacts: To simplify joint modelling across data sources, Simon and his colleagues restrict inputs to the most widely used sequencing technology (Illumina), excluding other measurement types (e.g., microarrays). 
- Data quality: Simon pointed out that they had to discard about half of the datasets because of poor quality. 

Despite all that, Simon was pleasantly surprised by how much signal was captured in the curated data. He noted that his appreciation of public sources grew through the process.

Nevertheless, he cautioned that some domains are unlikely to be fully served by public data. Neurology is a prominent example as samples are predominantly post-mortem, likely missing live effects. Still, he argued this should not be a reason not to try it out in the future.

#### Starting with a can of worms

Unstandardized reporting formats are a major hurdle in data collection. Jessica said that even a single trial’s data are often not deposited together, with pieces scattered across sources. What is more, as these fragments come from different trial sites and times, they can contradict each other. Thus, in some cases, they partnered with data providers to stitch everything into a single, coherent story.

<details closed>
<summary><u>Deciphering the reason for trial failure</u></summary>
<div style="border:1px solid #535353;border-radius: 7px;padding: 10px;margin: 5px;">
Clinical trial failure can mean different things: lack of efficacy, serious side effects, or simply failing to recruit enough patients - and sometimes the true reason remains unpublished. Adir explained that with sufficient data from similar trials, the likely cause can often be inferred. For example, a population shift between phase II and III may point to efficacy or safety problems in the new group. Conversely, if another drug with the same MOA is already approved, the MOA itself is less likely to be the issue. Their models are therefore designed to account for this label uncertainty.
</div>
</details>
<p></p>
<p></p>

Similarly, Raul noted that even data from company-internal trials is not as standardised as one would expect. Measurement processes often change across sites and over time, so values can not be directly compared.

Nevertheless, Jessica is finally starting to feel that the data processing is getting easier thanks to the internal tools and expertise that PhaseV developed. While everyone, of course, wishes for standardized deposition, Adir noted that the skill of processing data is what makes PhaseV unique. - Not everyone can take this can of worms and transform it into something useful for the industry. It is not enough to clean data - you must anticipate how it will be used in the future. For example, if labels are inferred, different downstream use‑cases may demand varying levels of interpretability about the inference process.

At the same time, it is also exciting to see that the community as a whole is shifting towards better reporting practices, Jessica explained. Previously, curation quality varied by source, with the NIH database being the easiest public source to work with. Electronic health records are another positive example, as national reporting standards have produced cleaner terminology[^footnote8] than is typical in clinical trials. CDISC has long advocated standardization in trials. As computational data processing is gaining in importance, these standards are finally seeing wider adoption and enforcement. With PhaseV being a member of CDISC, Jessica is eager to help improve the standardization alongside other involved parties, ranging from regulatory institutions to pharmaceutical companies. She is confident these standards will fundamentally change how data will be used.

On another note, with new textual data sources being increasingly used, Raul pointed out that also privacy and ethical concerns are being re-thought. For example, in the past it was common to manually sift social‑media posts to learn about patient needs. As automation dramatically increased the scale at which such analyses can be done, it became clear that specific ethical standards needed to be established (Cimiano, 2026).

## Key takeaways

With clinical trials being tightly regulated, more than just a well-performing model is needed for practical adoption. It is essential to understand both the standard process and the tradeoffs between different factors determining success. 

## References

- Cimiano, et al. Best practices for the collection and analysis of patient experience data from social media for patient-focused drug development. Frontiers in Medicine (2026).

## Footnotes

[^footnote1]: Many of his works are also published in scientific journals.
[^footnote2]: Their training data is composed of samples from both healthy and diseased donors, in approximately 7:3 ratio.
[^footnote3]: To make this possible, they collected a comprehensive patient database that can be used during inference. However, this data is not the primary information source for training. 
[^footnote4]: Of course, logistic barriers to performing clinical trials, such as partnering with hospitals, would not be solved.
[^footnote5]: Clinical trials are executed in two phases: First, a plan is designed and approved by ethical committees and regulatory bodies (e.g., FDA, EMA). Afterwards, the study is carried out according to the plan with limited flexibility at pre-defined decision points.
[^footnote6]: They do not train the model on clinical trial outcomes, and instead focus on reconstructing expression patterns observed in predominately healthy subjects. Thus, it is easier to design validations on clinical trials without the fear that model performance would be overestimated due to data leakage.
[^footnote7]: Single-cell data measures individual cells, while bulk data measures tissue samples, meaning that individual cells can not be distinguished. The former is thus very popular for identification of new therapeutic targets (i.e., genes that change in the affected cell type under disease).
[^footnote8]: In electronic health records, there are two commonly used standardized vocabularies: SNOMED CT and ICD. SNOMED CT is focused on capturing detailed clinical information about patients’ health status and performed procedures, with a granular description constructed from standard terms. In contrast, ICD is based on pre-defined categories, which were designed for statistical and billing purposes. However, neither standard is enforced by all countries and some national governments have also decided to create their own adapted variants of the terminology.
