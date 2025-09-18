---
date: 2025-09-10
categories:
  - Programming
---

# How I run an online business on AWS for less than $5/month

I've been working on starting several online applications - simple things like edit PDFs/some other task with Stripe integration. I'm using AWS as my cloud provider (just happens to be something I'm familiar with).

Previously, I'd be paying something like $50 USD/month per application.

Now, I've optimized my stack to run them for less than $5 USD/month each.

<!-- more -->

## Typical Setup

Typically, in a large organization, the stack would be something like:

- Backend: ECS or EKS
- DB: RDS
- Frontend: S3 + CloudFront

I deploy via Infrastructure-as-Code (IaC), and to keep things tidy, each application uses its own separate set of resources - one AWS RDS DB for each and so on. This isolates applications, and I can provision or destroy each application independently of the rest, with no dependencies between each one.

The above setup costs (all prices are for the `ap-southeast-1` region, based on 750 hours/month):

| Service                  | Price  | Notes                                                      |
| ------------------------ | ------ | ---------------------------------------------------------- |
| [ECS][ecs]               | $3.91  | 0.25 vCPU, 0.5GB RAM for [Fargate Spot instances][fargate] |
| [Static IP][vpc] for ECS | $3.75  | ECS task is in a public subnet                             |
| [RDS][rds]               | $18.75 | db.t4g.micro - the smallest                                |
| [ALB][alb]               | $16.88 |                                                            |
| S3                       | $0.00  | Frontend                                                   |
| Cloudfront               | $0.00  | Free tier includes 1TB of data transfer out per month      |

Total: $43.29 USD/month

??? note "Why is the ECS task in a public subnet?"

    The ECS task is placed in a public subnet for it to have outbound internet access, so we need to pay for the IPv4 address. Alternatively, it could be put in a private subnet, but then you'd either have to pay for a NAT Gateway, or use something like [fck-nat].

??? note "ECS without ALB"

    It is possible to run ECS without an ALB, by using CloudMap and a HTTP API Gateway as shown [here][ecs-without-alb]. However, Server Sent Events (SSE) are not supported by API Gateway, and so for my applications which use that (e.g. LLM streaming), it is not viable.

## Optimized Setup

After thinking through, I realized the pricey components could be swapped out:

- ECS: Replace with [App Runner], a container service that can automatically [scale vCPU usage to zero][app-runner-scale]. You only pay for the cached memory. Scaling down is fast - within a minute.
- RDS: Replace with a serverless Postgres provider - I use [Neon].
- ALB: Not required with App Runner.

The cost:

| Service    | Price  | Notes                                                                  |
| ---------- | ------ | ---------------------------------------------------------------------- |
| App Runner | ~$2.60 | $0.007/GB-hour idle, $0.064/vCPU-hour active. Based on 0.25vCPU/0.5GB. |
| DB (Neon)  | ~$0.50 | $0.14/CU-hour + $0.35/GB-month storage. First 50 hours free.           |
| S3         | ~$0    | Frontend                                                               |
| Cloudfront | ~$0    | Free tier includes 1TB of data transfer out per month                  |

_Note: For [Neon], the smallest configuration is 0.25CU, which is 0.25vCPU and 1GB RAM._

Total: ~$3.10 USD/month

## Compute: App Runner vs ECS

Assuming the App Runner instance (with 0.25vCPU and 0.5GB RAM) is continually active, this will cost $(\$0.064/4 + \$0.007/2) \times 750 = \$14.625$.

For ECS, an equivalent Fargate Spot instance together with the static IP and ALB would cost $\$3.91 + \$3.75 + \$16.88 = \$24.54$.

For low-moderate traffic, App Runner is the winner here.

_Note: It might be possible to use Cloudfront, CloudMap and ECS (with public IPs). This would still allow for SSE, and cost $\$3.91 + \$3.75 = \$7.66$, making it more attractive if the App Runner cost were to go above this. I haven't explored this yet._

## Database: Neon vs RDS

Neon starts to get expensive when the DB is being constantly queried.

If the database were to be active throughout the whole month, the cost (for the smallest 0.25CU instance, which has 0.25vCPU and 1GB RAM) would be $\$0.14/4 \times 750 = \$26.25$

In contrast, a RDS db.t4g.micro instance (with 2 vCPUs and 1GB RAM) costs $18.75.

So if application traffic picks up, I'm switching back to AWS RDS.

## FAQ

### Why not use AWS Lambdas?

The state of Lambdas has changed quite rapidly, and now container images are supported, as well as even wrapping an entire web framework (FastAPI/Express/Laravel) into a Lambda via the [AWS Lambda Web Adapter]. You do not pay anything for Lambdas when they are not in use (apart from ECR fees if you are using a container image). The Function URL allows Lmabdas to stream their responses, and Cloudfront supports Function URLs as an origin.

Unfortunately, the biggest drawback is still the cold-start.

I ran my backend on both App Runner and AWS Lambdas:

| Service    | Cold Start Time |
| ---------- | --------------- |
| App Runner | ~300ms          |
| Lambda     | ~6000ms         |

The UX is quite bad with such a long cold start time, and it is going to turn away a lot of potential users.

That being said, if you don't require SSE and can tolerate the cold starts, Lambdas can be cheaper than App Runner.

### What about AWS Lambdas with Provisioned Concurrency/SnapStart?

[Provisioned Concurrency] pre-initializes a set number of execution environments for your function, reducing cold start times significantly. [SnapStart] takes a snapshot of the initialized execution environment and uses it to create new execution environments, further reducing cold start times.

The base costs (assuming 0 incoming requests, based on a single 0.5GB instances) are:

| Service              | Cost        | Notes                                        |
| -------------------- | ----------- | -------------------------------------------- |
| App Runner           | $2.60/month | $0.007/GB-hour idle                          |
| Lambda (Provisioned) | $5.48/month | 2,628,000 seconds x 0.5GB x 0.0000041667 USD |
| Lambda (SnapStart)   | $2.03/month | 0.0000015046 per GB-second for cache         |

Unfortunately, SnapStart does not work with container images, which doesn't fit my use case.

### How about GCP's Cloud Run?

GCP Cloud Run is similar to AWS App Runner, and lets you run a container billed by the second. Unlike App Runner, it supports scaling to zero completely, meaning there is no monthly minimum. However, scaling to zero means that the container's memory is no longer allocated, which can lead to increased latency for cold starts.

To achieve the same latency characteristics as App Runner, Cloud Run supports keeping a minimum number of instances warm.

For the equivalent 0.25vCPU, 512MB RAM setup, the price for 1 month is

- vCPU: $\$0.0000025 \div 4 \times 2628000 = \$1.6425$
- Memory: $\$0.0000025 \div 2 \times 2628000 = \$3.285$

Total = $4.9275

While this is higher than App Runner's minimum cost ($2.60/month), it is possible to run the service completely on demand and only pay for what you use (albeit with long cold start times).

### Why not AWS Lightsail for the database?

AWS Lightsail (a VPC service) is a cheap way to run Postgres; the cheapest plan is $5/month. You'll need to manage updating and scaling yourself, however. Also, this makes my IaC a bit less isolated, since multiple applications are going to be sharing the same database - have to be careful to avoid using the same name for databases.

### Why not use a NoSQL DB like Firestore/DynamoDB?

I'm personally not a fan of NoSQL as there's less type-safety, less constraint enforcement and migrations are more troublesome. Also, with larger scale, you start paying for read/writes, unlike traditional SQL databases where you just pay for the runtime.

### Why not Aurora Serverless V2 for the DB?

Aurora Serverless v2 supports [auto-pause], which scales the instances to zero after inactivity. However, the reboot time is around 15 seconds, which is quite slow.

[ecs]: https://aws.amazon.com/ecs/pricing/
[fargate]: https://aws.amazon.com/fargate/pricing/
[rds]: https://aws.amazon.com/rds/pricing/
[vpc]: https://aws.amazon.com/vpc/pricing/
[alb]: https://aws.amazon.com/elasticloadbalancing/pricing/?nc=sn&loc=3
[fck-nat]: https://fck-nat.dev
[AWS Lambda Web Adapter]: https://github.com/awslabs/aws-lambda-web-adapter
[neon]: https://neon.com/
[auto-pause]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2-auto-pause.html
[api-gateway]: https://aws.amazon.com/api-gateway/pricing/
[App Runner]: https://aws.amazon.com/apprunner/
[SnapStart]: https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html
[Provisioned Concurrency]: https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html
[ecs-without-alb]: https://www.stacktape.com/blog/why-i-do-not-use-load-balancer
[app-runner-scale]: https://fgj.codes/posts/app-runner/
