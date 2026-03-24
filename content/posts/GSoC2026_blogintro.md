---
title: "My First Blog Post"
date: 2026-03-22T16:00:00-00:00
draft: false
tags: ["intro", "GSoC"]
categories: ["general"]
author: ""
description: "Welcome to my blog! This is my first post."
cover:
    image: ""
    alt: "GSoC Icon"
    caption: "GSoC"
    relative: true
---

## Welcome to My Blog! 

It finally happened. I have now been made a cog in the machine that is GSoC. 

This page will now exists as a platform for my peers and future colleagues to enjoy my GSoC journey. Whether it be failed pull requests, frustrating unsquashed commits or just simple grammar mistakes, I hope it will be helpful for all who endeavour to contribute to open source and academia. 

## What is GSoC?
GSoC (or Google Summer of Code) is a global online project run by Google. The focus of GSoC is to attract contributors to the open source software space. By allowing organisations to sumbit projects and accompanying mentors, GSoC empowers newcomers to the contribute to the vast and unknown world of open source software projects. 

## Project Selection

### What You Can Expect

On this page I will be keeping blogs focused on my recent GSoc 2026 application process. Should I be accepted as a contributor for the project I hope to work on, then there will be weekly updates kept on this blog. While the goal of keeping blogs to have a publically accessible record of project goals, accomplishments and remaining tasks, I hope to offer a more personal view on the highs and lows of the journey. As the contributor guide aptly states: "If you think you know everything, then you are not good enough for GSoC!". 

From my point of view this can not be more true! It is simply the case that few university programs in the world a can tailor a program for students in such a way that they are entirely prepared for anything a new code base throws at them. To me, that makes this project all the more exciting. No experience is as valuable as hands on development and getting to interact with contributors who have been a part of the open source community.

So to ensure that readers get a representative view of what the GSoC experience is like, especially for someone who has a prior knowledge and experiences in coding, the blog posts will not only include project updates but also some of the hilarious pitfalls, mistakes and general misery that a lack of thorough reading can cause.

### What's Next?

In my coming post I'm planning to write about my first pull request made to `SunPy/radiospectra`. 

### Coden snapshot from my first PR!

My initial thought was that this would be a very simple job! I mean, how difficult can an elif be right?

```python
 elif ("SOLO" in cdf_globals.get("Project", "")[0]):
            data_type = cdf_globals.get("Data_type", [""])[0]
            data_descriptor = cdf_globals.get("Descriptor", "")[0]
            if ("RPW-HFR-SURV" not in data_descriptor
            and "RPW-TNR-SURV-FLUX" not in data_descriptor):
                    raise ValueError(
                        f"Currently radiospectra supports Level 2 HFR survey data "
                        "and Level 3 HFR, TNR survey data the file "
                        f'{file.name} is {cdf_globals.get("Logical_source_description", [""])[0]}'
                    )
            if("L3" in data_type):
                epoch = cdf.varget("Epoch")
                times = Time("J2000.0") + epoch * u.ns
                freqs = cdf.varget("FREQUENCY") << u.Unit(
                    cdf.varattsget("FREQUENCY")["UNITS"]
                )
```

---

Thanks for reading!