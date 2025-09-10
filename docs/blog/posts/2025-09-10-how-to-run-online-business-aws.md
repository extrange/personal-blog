---
date: 2025-09-10
categories:
  - Programming
---

# How I run an online business on AWS for free (almost)

I've been working on starting several online applications - simple things like edit PDFs/some other task with Stripe integration. I'm using AWS as my cloud provider (just happens to be something I'm familiar with).

Previously, I'd be paying something like $50 USD/month per application.

Now, I've optimized my stack to run them for almost nothing.

<!-- more -->

## Typical Setup

Typically, in a large organization, the stack would be something like:

- Backend: ECS (or EKS)
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

_Note: The ECS task needs to be in a public subnet for it to have outbound internet access. Alternatively, it could be put in a private subnet, but then you'd either have to pay for a NAT Gateway, or use something like [fck-nat]._

## Optimized Setup

I thought through the above, and realized the pricey components could be swapped out:

- ECS: Replace with AWS Lambdas. I use a container image with the [AWS Lambda Web Adapter], which lets me run FastAPI applications.
- RDS: Replace with a serverless Postgres provider - I use [Neon].
- ALB: Not required with Lambdas.

The setup above costs:

| Service     | Price  | Notes                                                 |
| ----------- | ------ | ----------------------------------------------------- |
| Lambda      | ~$0    | Effectively free for low usage                        |
| API Gateway | ~$0    | [$1/million][api-gateway] requests                    |
| DB (Neon)   | ~$0.50 | $0.14/CU-hour + $0.35/GB-month storage                |
| S3          | ~$0    | Frontend                                              |
| Cloudfront  | ~$0    | Free tier includes 1TB of data transfer out per month |

_Note: For [Neon], the smallest configuration is 0.25CU, which is 0.25vCPU and 1GB RAM. Assuming the DB is used continuously (highest cost scenario), this would be $26.25/month. The default scale-down time is 5 minutes._

Total: ~$0.50 USD/month

## Notes

**AWS Lightsail** is a cheap way to run Postgres; the cheapest plan is $5/month. You'll need to manage updating and scaling yourself, however.

Neon starts to get expensive when the DB is being constantly queried - if the costs goes up more than $18.75/month (price of a RDS db.t4g.micro instance), I'll probably switch back.

API Gateway (and thus Lambdas behind it) do not support SSE. However, it is possible to call the Lambda function URL directly. Note that the endpoint should authenticate the user accordingly, since there is no API Gateway in front.

## FAQ

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
