---
date: 2025-09-18
categories:
  - Programming
---

# Lessons From My First Product Launch

Today I launched [CloudVise], an AI advisor giving personalized advice across multiple topics. It was a long journey, starting all the way back in July.

Here are some lessons I learnt.

<!-- more -->

## Timeframes

I started work on the product right after I left my previous company, at the start of July.

The first 1-2 weeks were spent reading some nice fantasy books, relaxing, and brainstorming. Eventually I decided I would make a skeleton of an app first - something that could handle payments and logins, on a Python backend (FastAPI) and a NextJS frontend, hosted on AWS.

Initially I was very obsessed with Infrastructure-as-Code (IaC), since in my previous company, a lot of the deployment was manual. I started with a production-grade, scalable setup on AWS (with load balancers, containers via Elastic Container Service, and databases vs Relational Database Service).

After I set that up, I realized that it would cost me ~$50/month just for hosting a single product. So, I spent another week optimizing that setup (I managed to drop the monthly cost per product to $2.50 - you can read about that [here][optimizing-cost]).

I worked on the frontend in the last week prior to the product launch. Using AI tools was quite a big help here (I'm not very familiar with TailwindCSS).

## Takeaways

### Having a solid backend is important

Most people brush aside the backend as it is not something obvious to users, however from my past experience, a misfunctioning/unreliable backend can really turn users away. I was fortunate to have a codebase I had spent a lot of time refining over the previous months which I could adapt for this purpose.

A well designed backend should:

- be simple to understand (modular code)
- have functions which do only one thing
- not hardcode variables (so you can develop locally)
- have unit tests (ideally)

The usual principles of Clean Code apply.

### Automated deployments speed up development time

I use Github Actions for CI/CD, using OpenTofu for deploying infrastructure. Once I make changes to the `dev` branch, merging them to `prod` triggers the pipeline and the production site is updated ~5 minutes later.

This is very helpful for testing production-only things like Stripe payments on the live account, or Google Analytics.

### Nice frontend stuff

Tailwind CSS (for theming), Shadcn (for components) and Lucide Icons are a great combination. It's easy to swap themes via [tweakcn], dark mode comes for free, and mainstream LLMs are very familiar with this stack.

## Random thoughts about handling long-running jobs on the backend

I was randomly thinking about the best way to handle the scenario where the backend needs to make an API call to a vendor which might take a long time (e.g. video generation).

I initially thought we could just have the frontend wait for the backend to complete, but I realized this wasn't really feasible because long running HTTP connections can time-out on many layers (API Gateway has a 29s timeout, App Runner has a 120s hard timeout). What happens to the backend result if the connection is interrupted, but the vendor's request finishes?

There are 2 ways to solve the problem. Both involve asynchronous processing.

The first is to use a webhook from the vendor. This way, the vendor can notify the backend when the long-running job is complete, and the backend can then update the database accordingly. Meanwhile, the frontend continuously polls a backend endpoint to check the status of the job.

If the vendor does not have a webhook, then the second best option is to use a queue (e.g. Simple Queue Service). A queue offers features like message retention, dead letter queues to handle failures, and FIFO ordering.

In particular, an implementation of queue + function system (SQS + Lambda) for a low price could be:

Queue:

- message retention period 12 hours
- default visibility: 30s (how long we will wait for a worker to process, before making the message available to other workers again)
- maxReceives: 900 -> 1800s (30min) is max time we can wait for the vendor
- DLQ after that

A message comes in.

Worker (a Lambda function):

- first, check timestamp: if > 20min in queue, mark failed and send to DLQ
- check job status from the vendor:
  - Success: get result, update DB, remove message.
  - Pending: if this is the first run, block for 30s, then set the visibility timeout to something short like 5s. On each retry, check message age. If < 60s old → 2s visibility; if < 5m → 5–10s; if < 20m → 15–30s.
  - Failed: send to DLQ, remove message.

DLQ handler:

- Update DB, remove message.

In the interest of saving money I checked the costs on GCP, which offers Cloud Run Worker Pools. The cost: 0.000011244 × 2,628,000 = 29.549232 (≈ $29.55). Minimum machine size: 1 vCPU, 512 MB RAM. This is still pretty expensive compared to using AWS Lambdas.

[CloudVise]: https://cloudvise.io
[optimizing-cost]: ./2025-09-10-how-to-run-online-business-aws.md
[tweakcn]: https://tweakcn.com
