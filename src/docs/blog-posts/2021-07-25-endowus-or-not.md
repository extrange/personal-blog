# To Endowus, Or Not?

[Endowus][endowus] has been making waves in the robo-advisor market in Singapore, hitting $1 billion in assets under management (AUM) recently.

It offers tailored investment solutions, customized for your risk appetite. Its portfolios are constructed from institutional-level fund classes, so fees are lower. Endowus also rebates trailer fees they receive from funds, so you pay even less. Finally, you can even build your own portfolio, using funds from PIMCO to Dimensional.

With that in mind, should you switch from IBKR to Endowus?

## Endowus

Of the robo-advisors in Singapore, Endowus is the only one offering [institutional level funds][fund-smart-in-depth] (the rest, such as [Syfe][syfe] or [Stashaway][stashaway], use ETFs). Institutional-level funds may offer [lower][institutional-level-funds] costs than their retail counterparts.

Endowus is also the only way you can access to funds from [Dimensional][dimensional], a world-wide mutual fund company boasting Nobel laureates such as Myron Scholes[^scholes]. Most of the Dimensional funds are based off broad indexes such as the MSCI World Index, the ACWI or the AGGU (for fixed income).

Endowus also offers [Cash Smart][cash-smart], their version of fixed deposit, with varying levels of risk and returns up to 2% pa.

There are also no currency conversion fees with Endowus - all their funds are denominated in SGD. Presumably, the conversion to USD happens within the fund internally and is charged in the net expense ratio, but even that is low (Endowus' fund's expense ratios are ~0.5% pa).

Instead, what Endowus charges is an *access fee*, ranging from 0.25% - 0.6% pa, charged quarterly. This is comparable to the 0.4% - 0.65% pa charged by [Syfe][syfe-pricing], the 0.2 - 0.8% charged by [Stashaway][stashaway-pricing] and the 0.3 - 0.5% pa charged by [Kristal][kristal-pricing].

## Interactive Brokers

[Interactive Brokers][ibkr] (IBKR) is the largest electronic trading platform in the US. In June 2021, they managed [$363.5 billion][ibkr-aum] in assets, with over 2,471,000 trades executed daily.

Unlike Endowus, which is at heart a robo-advisor, IBKR is a fully featured broker, giving you access to stocks, ETFs, futures, currency, derivatives and more, across global markets.

The [commissions][ibkr-commissions] IBKR charges are highly competitive and are one of the lowest in the market. There is even a [commission-free][ibkr-lite] account, which is sadly unavailable in Singapore.

IBKR also recently slashed its monthly inactivity fees - there are now [no annual or monthly charges][ibkr-monthly-fees] to use the platform. You therefore only pay on each trade (the bid-ask spread + commissions + exchange fees).

With this flexibility however, comes some drawbacks:

- You must convert currency yourself (although the rates are one of the best[^ibkr-currency])
- You must decide which securities to purchase
- Rebalancing must be done by yourself
- A maximum of 1 free withdrawal a month, with fees charged subsequently

## Comparison

Let's summarize the information above:

|                       | Endowus                                   | IBKR                                           |
|-----------------------|-------------------------------------------|------------------------------------------------|
| Type                  | Robo-Advisor                              | Fully-featured Broker                          |
| Founded               | 2017                                      | 1978                                           |
| AUM                   | $1bn                                      | $363.5bn                                       |
| What you can buy      | Institional-Level, SGD Denominated funds  | Stocks, ETFs, mutual funds, bonds, derivatives |
| Annual Fees           | 0.25 - 0.6%                               | None                                           |
| Transaction Fees      | None                                      | Commission + Exchange Fee + Bid/Ask Spread     |
| Rebalancing           | Automatic, free                           | Manual                                         |
| Currency Conversion   | N/A                                       | Manual[^ibkr-currency]                         |
| Custodian             | UOB Kay Hian (trust account in your name) | IB LLC                                         |
| Custodian Bond Rating | [Aa1 (Moody's)[^uob-rating]][uob-rating]  | [BBB+ (S&P)][ibkr-rating]                      |
| Withdrawals           | Free                                      | 1 free a month, subsequent charged ~USD $10    |

Here is what you pay per year, assuming you invest 25% of the amount each quarter, until you reach the full amount by the end of the year[^assumptions].

| Total Amount | Endowus | IBKR (1 ticker) | IBKR (4 tickers) |
|--------------|---------|-----------------|------------------|
| $10,000      | $60     | ~$16            | ~$64             |
| $$100,000    | $600    | ~$50            | ~$64             |
| $1,000,000   | $3,500  | ~$500           | ~$520            |

For a small amount (~$10,000), Endowus and IBKR cost about the same. But as you invest more, IBKR's pricing becomes more attractive.

Note that for IBKR, for small amounts, buying more stocks costs more. For large amounts however, the price is essentially identical.

Endowus' fees are the same, regardless of how many individual funds you purchase.

## Verdict

With all this in mind, which is better - Endowus or IBKR?

Personally, I would go with Endowus for small amounts up to $500,000. Although I pay more fees, I think of this as a convenience factor for:

- being able to invest in Dimensional
- automatic rebalancing
- no currency conversion required

For larger amounts above $500,000, the difference in commissions becomes significant (about $3,000 starting from $1M in assets). In that scenario, taking the time to DIY your portfolio in IBKR makes more sense.

For ideas on what to buy, check out my suggestions for [IBKR](2021-01-16-my-investment-portfolio.md) and [Endowus](2021-07-25-my-endowus-portfolio.md).

[endowus]: https://endowus.com/
[fund-smart-in-depth]: https://endowus.com/insights/endowus-fund-smart-in-depth-review/
[syfe]: https://www.syfe.com/core-growth
[stashaway]: https://www.stashaway.sg/how-we-invest
[institutional-level-funds]: https://www.cruxinvestor.com/articles/institutional-vs-retail-investors
[dimensional]: https://sg.dimensional.com/
[cash-smart]: https://endowus.com/cash-smart
[syfe-pricing]: https://www.syfe.com/pricing
[stashaway-pricing]: https://www.stashaway.sg/pricing
[kristal-pricing]: https://kristal.ai/wp-content/themes/di_kristal/documents/02_2021-Kristal_Freedom_Pricing-Singapore.pdf
[ibkr-aum]: https://investors.interactivebrokers.com/ir/main.php?file=latestMetricPR
[ibkr]: https://www.interactivebrokers.com/en/home.php
[ibkr-commissions]: https://www.interactivebrokers.com/en/index.php?f=1340
[ibkr-lite]: https://www.interactivebrokers.com/en/index.php?f=45196
[ibkr-monthly-fees]: https://www.interactivebrokers.com/en/index.php?f=4969
[uob-rating]: https://www.uobgroup.com/investor-relations/capital-and-funding-information/credit-ratings.html
[ibkr-rating]: https://www.interactivebrokers.com/en/index.php?f=2334

[^scholes]: Co-originator of the Black-Scholes options pricing model, used widely for hedging, pricing and speculative purposes in all markets globally.
[^uob-rating]: This is the rating for UOB's Long-Term Bank Deposits by Moody's.
[^ibkr-currency]: IBKR's rates for currency exchange are highly [competitive](https://investmentmoats.com/uncategorized/convert-currencies-interactive-brokers/).
[^assumptions]: The cost for IBKR includes brokerage commissions, exchange fees, and an estimate of the bid-ask spread.