# About Myself

<figure>
  <img src="/static/images/thoreau-quote.jpg" alt="Henry David Thoreau" loading="lazy"/>
  <figcaption style="font-size: small;margin-top: 5px">Credits: <a href="https://www.flickr.com/people/23094783@N03">Alex</a> of Ithaca, NY (<a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>)</figcaption>
</figure>

My interests include [computing](#computing), [nutrition](#nutrition), [spirituality](#spirituality) and [sports](#sports).

## Computing

**Projects and My Setup**

I enjoy programming as well as tinkering with computer hardware and servers. I run a [server in my home][server], on which I self-host services such as [virtual machines][vm], file storage/sharing, torrents, an administrative interface and more.

I primarily work on full stack applications, mainly in React with Javascript/Typescript, with Django as the backend. I am also exploring [algorithmic trading][ibkr-docker].

I run [Fedora][fedora] on both my [server][server] and personal computers.

The field of Natural Language Processing and in particular, the latest developments in [transformer models][huggingface-models] continue to fascinate me, in part because research in this field seems to be gaining almost human-like abilities and intelligence. I have [written][language-models] some of my thoughts on whether these models possess intelligence, as well as other interesting conclusions.

I type in the Dvorak keyboard layout, and use Vim or its keybindings, mainly for [ergonomicity][ergonomics].

**The Joys of Coding**

On some days, the rain and thunder might be pouring outside, while I fix and commit code, taking care to write each subroutine and function as elegantly as possible, with no unnecessary load on the computer. This strive towards perfection annoyed even myself initially, as I often got stuck on a particular feature for days. However, it soon began to feel sort of like a meditative process, almost Zen-like, where the goal was not in the resolution of the issue, but rather in the journey itself, and the numerous libraries I picked up along the way.

To me, coding is about building and fixing structures. Unlike in the real world, however, one can build anything imaginable in code. Any form of control or automation so desired is attainable, limited only by the laws of logic.

The collaborative process in coding is unique to the field. We write programs to automate menial tasks. Later on, we release them to the public domain, where other people build larger programs on top of them, and in turn release them. This eventually culminates in large but polished libraries such as React and Django, or refinements to the languages themselves such as ES6. When you `import React from 'react'`, destructure a variable with `...` or `debounce` a function, you are calling upon the work of thousands of people who have developed these facilities, sometimes to solve the very same problem you are facing, and almost instantaneously. It is almost as if you are coding with the world at large.

**My Computing Journey**

I started out by reading books about computer hacking. Long ago, I borrowed a book on computer security (it was a thick book with a picture of a chessboard). I read about NMAP, TCP/IP, exploits on the IIS server (CodeRed), Windows LANMAN...though I didn't understand much then, I knew I really wanted to learn more about computers.

> "The programmer, like the poet, works only slightly removed from pure thought-stuff. He builds his castles in the air, from air, creating by exertion of the imagination. Few media of creation are so flexible, so easy to polish and rework, so readily capable of realizing grand conceptual structures." - Frederic P. Brooks

I was interested in computers and IT since I was in primary school. The web was in its infancy then; I still remember using 56kbps dialup. Ironically, most of my interest came about when my parents locked my computer and I had to figure out ways of circumvention (booting Linux, keyloggers...). I learnt about networking from trying to configure the routers in my house mostly by trial and error - those IT people my parents called charged something north of $50 just for tweaking settings like DHCP or DNS and security. The 1999 movie 'The Matrix' was also a big inspiration to me.

<figure>
  <img src="/static/images/art-computer-virus-research-defence.jpg" alt="The Art of Computer Virus Research and Defence" loading="lazy"/>
</figure>

I read [The Art of Computer Virus Research and Defence](https://www.goodreads.com/book/show/746747.The_Art_of_Computer_Virus_Research_and_Defense) sometime in the 2000s. It read like a novel, detailing the different methods virus writers would use, and the catch up game antivirus vendors would play. Some of the methods (like polymorphic encryption, virtual machines) used by the virus writers were incredibly complicated, but yet, amazingly, the authors of the book were able to provide a detection heuristic for them.

Later on, my portable hard drive, filled with most of my personal data collected over many years, crashed. My diaries, personal notes, photos were gone. That was when I began reading on filesystems ($MFT, streams, MBR/GPT) and data recovery (I couldn't buy EnCase so I made do with dd and a hex editor). Although I wasn't successful in recovering my data, I finally understood how filesystems and their fault tolerance mechanisms worked.

<figure>
  <img src="/static/images/elevated.jpg" alt="Elevated by rgba" loading="lazy"/>
  <figcaption>This screenshot (20kB) is larger than the <a href="https://www.youtube.com/watch?v=jB0vBmiTr6o">program</a> (4kB)</figcaption>
</figure>

I briefly read about x86 assembly and reverse engineering. I was inspired by the crackers of the day (Razor 1911, FAiRLiGHT, DEViANCE) and the demoscene. People could do crazy things with pure machine code - rgba made an entire mountain simulation with music in 4kB! I tried briefly reverse engineering some small programs. I found it rather complicated, and although I did succeed with some (patching with NOPs), I never really continued programming with assembly.

In high school I played mostly with the Windows OS and its internals. I had fun with bruteforcing Windows passwords with tools like L0phtCrack/Cain and Abel. It was also my introduction to the world of cryptography, spurred further by allegations that the US government was decrypting internet communications and had the capability to decrypt 128-bit AES.

I've written a program to search for image duplicates via convolutional neural networks and cosine similarity in Keras. I've also reversed engineered my house DVR using Wireshark and the sockets library in Python.

## Nutrition

In recent years I have become much more conscious of what I eat, in part due to my medical background as well as from discussions with my colleagues. I believe a healthy diet not only affects the body, but the mind and its clarity as well.

[My diet][my-diet] has been varying over the years, but it is mainly a combination of complex carbohydrates, protein sources, fibre and healthy fat.

## Spirituality

I'm a big fan of Alan Watts, an American who was deeply involved in the promotion of Japanese Zen to the world. His [videos](https://www.youtube.com/watch?v=khOaAHK7efc) and [writings](https://www.goodreads.com/book/show/514210.The_Way_of_Zen) are frank, witty and hint at the beauty of his thought.

[My worldview](blog/posts/2022-03-03-determinism-and-stoicism.md) aligns most closely with Stoicism, and I am exploring Vipassana and Zen.

I attended a [10 day meditation retreat][meditation-retreat] in July 2022.

## Sports

I primarily gym and run, and play badminton. I strive to go [mountaineering](mountaineering.md) or hiking overseas once a year - the experience of raw nature at her best and worst is unforgettable.

Recently, I have found [skiing][skiing] to be quite enjoyable.

[server]: blog/posts/2022-05-22-my-self-hosting-journey.md
[vm]: blog/posts/2022-07-10-win11-vm-gpu-passthrough.md
[fedora]: https://getfedora.org/
[language-models]: blog/posts/2022-03-30-artificial-intelligence-language-models.md
[huggingface-models]: https://huggingface.co/models
[ergonomics]: blog/posts/2022-02-27-my-computing-philosophy.md#ergonomicity
[my-diet]: blog/posts/2022-08-01-my-diet.md
[meditation-retreat]: blog/posts/2022-08-05-vipassana-meditation-retreat.md
[mountaineering]: mountaineering.md
[skiing]: blog/posts/2021-12-25-skiing-switzerland.md
[ibkr-docker]: https://github.com/extrange/ibkr-docker
