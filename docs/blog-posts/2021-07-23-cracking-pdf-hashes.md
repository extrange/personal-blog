---
tags:
  - Programming
---
# Cracking PDF Hashes with `hashcat`

Do you have a PDF document lying around somewhere, but it's encrypted and you've forgotten the password to it?

[`hashcat`][hashcat] is a great open-source hash cracker with GPU acceleration. It also comes with features such as masking, dictionary attacks and even [statistical methods][statsprocessor] of password guessing. It also supports 300+ hash types (e.g. SHA-1, MD5, WPA, Django...) out of the box.

Don't use this for unlawful purposes!

## Extracting the hash from the PDF

First, we need to extract the password hash from the PDF. There's an online tool for this, but for now let's use this python script ([pdf2john.py][pdf2john]).

Run it with `python pdf2john.py <your-pdf-file>`.

The output should resemble something like this:

```text linenums="1"
b'aa.pdf':b'$pdf$4*4*128*-1028*1*16*51cacf728db0cc489bd42a56dd58d87c*32*fa9ce7f2daef91b171ec19e04edc00ba00000000000000000000000000000000*32*c431fab9cc5ef7b59c244b61b745f71ac5ba427b1b9102da468e77127f1e69d6':::::b'D:\\Desktop\\<your PDF file>.pdf'
```

We're only interested in the second part (beginning with `$pdf$4...` up till `...69d6`). So, let's copy that out:

```text linenums="1"
$pdf$4*4*128*-1028*1*16*51cacf728db0cc489bd42a56dd58d87c*32*fa9ce7f2daef91b171ec19e04edc00ba00000000000000000000000000000000*32*c431fab9cc5ef7b59c244b61b745f71ac5ba427b1b9102da468e77127f1e69d6
```

This is the hash we'll supply to `hashcat` later on.

## Starting brute force with `hashcat`

First, grab the latest copy of `hashcat` from [here][hashcat].

This command runs a brute force attack on the hash (up till the maximum number of characters):

`hashcat -a 3 -m 10500 '<hash>'` (note: the hash must be in quotes, or else some OSes might interpret the `$` as a variable)

Let's break it down.

`-a` specifies the attack mode. In this case, `3` indicates brute force.

`-m` specifies the type of hash. `hashcat` can actually autodetect the hash type, but for this purpose, we'll specify it as as `10500`, which is `PDF 1.4 - 1.6 (Acrobat 5 - 8)`.

`hashcat` also supports masking options. So if you wanted to try all lowercase alphanumeric passwords (a-z, 0-9) up to 10 characters, you could do

```.\hashcat -a 3 -1 ?l?d -i -m 10500 '<hash>' ?1?1?1?1?1?1?1?1?1?1?1?1```

`-1` specifies the character set in the first position (`hashcat` supports multiple character sets). In this case, `?l` refers to the set `abcde...xyz`, and `?d` refers to all digits 0-9.

`-i` specifies that we want to progressively try the mask, starting from `--increment-min` (default 1). What this does is it will try only 1 character of the mask (e.g. `a`), then 2, up till `--increment-max` (default being the length of the mask, e.g. `zzzzzzzzzz`).

`?1?1?1?1?1?1?1?1?1?1?1?1` is the mask itself. `?1` refers to the character set in the first position, that we specified above with `-1`.

<figure>
  <img src="/static/images/2021-07-23/hashcat.jpg" alt="Cracking speed on my GTX 970" loading="lazy"/>
  <figcaption>Cracking speed on my GTX 970</figcaption>
</figure>

<figure>
  <img src="/static/images/2021-07-23/a100.jpg" alt="For comparison, cracking speed on an A100 on GCloud (approx 10x speedup)" loading="lazy"/>
  <figcaption>For comparison, cracking speed on an A100 on GCloud (approx 10x speedup)</figcaption>
</figure>

And that's it! Password cracking is exponentially slower with regards to the length of the password[^limits], so any clues as to the content of the password will speed it up greatly.


[hashcat]: https://hashcat.net/hashcat/
[statsprocessor]: https://hashcat.net/wiki/doku.php?id=statsprocessor
[pdf2john]: https://github.com/truongkma/ctf-tools/blob/master/John/run/pdf2john.py
[^limits]: Theoretically, a 51-character alphanumeric, case-sensitive password would be [uncrackable.](https://en.wikipedia.org/wiki/Transcomputational_problem)
