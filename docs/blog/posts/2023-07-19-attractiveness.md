---
categories:
    - Philosophy
date: 2023-07-19
---

# On Attractiveness

Recently, in my country, there has been a spate of politicians getting involved in extramarital affairs. This got me thinking more deeply about how we rate other people in terms of attractiveness, and whether a **total order** of the individual's ranking exists.

In mathematics, a total order describes a set $S$ of elements which fulfill the following properties for all $a$, $b$ and $c$ in $S$:

1. $a \le a$ (reflexivity)
2. If $a \le b$ and $b \le c$ then $a \le c$ (transitivity)
3. If $a \le b$ and $b \le a$ then $a = b$ (antisymmetry)
4. Either $a \le b$ or $b = a$ (strongly connectedness)

For the purposes of this article, I am referring to our ranking of other people, and not the global/societal ranking, as the latter may not even exist (people have different preferences, so there is no global order).

In this article, I put forward the idea that our subjective ranking of other people might actually lack items 2 (transitivity) and 4 (strongly connectedness).

## Transitivity

If Person A is more attractive than Person B, and Person B is more attractive than Person C, then mathematically speaking, Person A should be more attractive than Person C.

This is a big assumption we take for granted, however.

Suppose you give each person a set of properties $P$, and a score $s_i$, where $0 \le s_i \le 1$, associated with each property $P_1 \dots P_n$. The total score for that person may be taken as:

$$
\sum_{i=1}^n s_i
$$

Suppose further that you value some properties more than others. You therefore assign each property $P_i$ a weight $w_i$, where $0 \le w_i \le 1$. The total score for that person now becomes:

$$
\sum_{i=1}^n s_i \cdot w_i
$$

Everything is great! You can now rank individual attractiveness on a linear scale.

This however, depends on the following assumptions, which are not always true:

-   The weights $w_i$ we assign to each property, are the same from person to person.
-   Certain properties are correlated, and the score of a property can actually influence the weight of that or other properties. For example, if you like music, you may give a professional pianist a higher weight in $P_{music}$.
-   People actually (consciously or not) rate other people using such a model.

If any of these assumptions don't hold, then the property of transitivity may not hold.

## Strongly Connectedness

The principle of strong connectedness states that for any two elements, either one is greater than or equal to the other, or they are equal. This suggests a clearly defined hierarchy of attractiveness. Mathematically, for persons A and B, either of the following must be true:

$$
\begin{equation*}
A \le B
\quad
{or}
\quad
A = B
\end{equation*}
$$

However, attractiveness may more closely resembles a partial order - an ordering where it is not always possible to compare two elements.

Take for example, Person A, who scores $0.80$, and Person B, who scores $0.79$. Is Person B really ranked lower than Person A? Depending on your mood, and various other factors, they could rank equal or even higher than Person A.

So strongly connectedness may not even hold!

## Conclusion

Taking the above into consideration, a total order may not exist for an individual's ranking of attractiveness. This means that trying to find the 'most attractive' person could be a futile goal - without a total order, such a task is impossible!
