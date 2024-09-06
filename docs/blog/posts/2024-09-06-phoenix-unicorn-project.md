---
date: 2024-09-06
categories:
    - Books
---

# Book Summary: The Phoenix Project, The Unicorn Project, The DevOps Handbook (The Three Ways, Excerpt)

These three books are part of a series on DevOps, the first two through an engaging story about how the protagonists turn around a failing company by reducing lead times for deployments.

One of the companies I worked for had an uncanny resemblance to the events described in the books (particularly The Unicorn Project).

<!-- more -->

## The Phoenix Project

Similar to [The Goal], one releases work based on how fast the bottleneck resource can consume it, and not on the availability of the first station.

In this story, Brent is the bottleneck. Part of applying the 5 Step Process of Ongoing Improvement in this scenario is to ensure that the constraint is not allowed to be wasting any time:

- It should never be waiting on any other resource for anything
- It should always be working on the highest priority commitment

The Kanban board is useful is this regard, as it helps visualize and limit the flow of work to the constraint.

Being able to take needless work out of the system is more important than being able to put more work into the system. Guide this process by outcomes - not processes or controls. Audit work is one example - it does not increase throughput.

**The Four Types of Work**

-   Business Projects: Business initiatives, most of the development work.
-   IT Operations Projects: Infrastructure and IT Operations. Creating new environments, automating things etc. Often not tracked properly. These create problems when Operations are already under stress.
-   Changes: Often generated from the two previous types of work. Updating and changing different systems.
-   Unplanned work: Incidents and problems caused by technical debt. This comes at the expense of planned work.

## The Unicorn Project/DevOps Handbook

The Central Conflict: Development is tasked with responding to changes in the market and deploying features as quickly as possible. IT Operations, on the other hand, is tasked with providing customers with IT service that is stable, reliable and secure. These two goals are diametrically opposed.

The Value Stream: The sequence of activities an organization undertakes to deliver upon a customer request. This is measured by three metrics: lead time, process time (or touch time), and percent complete and accurate (%C/A).

### The Three Ways

**Flow**. This increases the speed of work from Development, to Operations, to the customer.

- Make work visible: Kanban boards, limiting WIP by setting column limits
- Reduce batch sizes: Small batch sizes decrease WIP, and allow faster detection of errors.
- Reduce handoffs: Many handoffs cause a loss of context as to the goal actually being sought. E.g. multiple emails required for approvals and so on.

Typical progression of constraints in an organization:

- Environment Creation
- Code Deployment
- Test setup and run
- Overly tight architecture (code changes requiring approvals)
- Development/Product Owners (the ideal area where constraints should lie)

**Feedback**. Enables fast and constant flow of feedback from Operations to Development.

- Telemetry: Automated build, integration and tests provide early feedback on failures.
- Swarming: When a problem is identified, all developers are alerted. This shares knowledge and prevents problems from spreading throughout the company (Toyota Andon cord example).
- Push Quality Closer to the Source: Allow developers to run tests themselves, instead of requiring QA.
- Optimize for Downstream Work Centers: Prioritize operational, non-functional requirements (e.g. architecture, performance, security) as much as user features.

**Continual Learning and Experimentation**. The creation of a high-trust culture, reinforcing that we are all learners who must take risks in our daily work. 

- Blameless post-mortems: By removing blame, you remove fear; by removing fear, you enable honesty; and honesty enables prevention.
- Institutionalize the improvement of daily work: Reduce technical debt. E.g. reserving cycles in each development interval, or scheduling _kaizen blitzes_.
- Transform local discoveries into global improvements: Share code, post-mortems
- Stress test: Inject network failures, server errors to increase resilience.


[The Goal]: 2024-09-06-the-goal.md
