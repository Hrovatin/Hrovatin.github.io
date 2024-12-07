---
title: "Saving time in open-source"
#date: YYYY-MM-DD HH:MM:SS +/-TTTT
categories: [Coding]
tags: [open source, python]     # TAG names should always be lowercase
description: Following the trail of best practices.
media_subpath: /assets/img/2024-11-25-open_source_packages/
image:
  path: zen_of_python_ink.jpg
  alt: <b>The Zen of Python.</b><br>Illustration of PEP 20 principles in sumi-e (Japanese brush painting) style.

---
![Desktop View](pep20.jpg){: width="500" alt="abc" .shadow}
_<b>Figure 1:</b> text_

![Desktop View](reddit_best_practices.jpg){: width="800" alt="abc" .shadow}
_<b>Figure 2:</b> text_

![Desktop View](commit_messages.jpg){: width="150" alt="abc" .shadow}
_<b>Figure 3:</b> text_

![Desktop View](sheep_coding.jpg){: width="300" alt="abc" .shadow}
_<b>Figure 4:</b> text_

![Desktop View](git_bisect.jpg){: width="300" alt="abc" .shadow}
_<b>Figure 5:</b> text_

![Desktop View](hypothesis.jpg){: width="700" alt="abc" .shadow}
_<b>Figure 6:</b> text_

![Desktop View](emoji_messages.jpg){: width="800" alt="abc" .shadow}
_<b>Figure 7:</b> text_

t[^footnote1][^footnote2][^footnote3]

## Footnotes
[^footnote1]: When we spoke in November of 2024, Lukas suggested r/programming and r/Python as well as r/ExperiencedDevs for more career-oriented discussions. However, he noted that communities change through time, prompting one to find new ones. He also recommended the blogs of Will McGugan, the main developer of Rich package for formatting terminal outputs, Tushar Sadhwani, and Charlie Marsh, a developer of Ruff linting package.
[^footnote2]: There is no way to specify opt-out dependencies that would be installed by default except if actively opted out. For example, this would be beneficial for user-statistics telemetry, where it is desired to increase the number of users prepared to share their data.
[^footnote3]: Integration tests often have extended runtimes. This can be mitigated with smaller input datasets. To enable a reliable assessment of output quality, one must find a good balance between a smaller dataset size and the naturalness of the data properties. Moreover, integration tests can be sped up by buying faster runners for GitHub actions.
