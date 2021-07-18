# About Myself

<figure>
  <img src="/static/images/thoreau-quote.jpg" alt="Henry David Thoreau" loading="lazy"/>
  <figcaption style="font-size: small;margin-top: 5px">Credits: <a href="https://www.flickr.com/people/23094783@N03">Alex</a> of Ithaca, NY (<a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>)</figcaption>
</figure>

I work as a doctor in Singapore. I've all sorts of interests and hobbies, from philosophy, photography to programming. What follows is a bit about my life and why I like programming.

## Writing at the speed of thought

I used to dream about building a device which could record your thoughts.

Suppose you were out on a run, and an idea popped into your head. It would be quite inconvenient to stop, take out your phone or pen, and jot down your thoughts - the act of recording interrupts the flow.

Imagine instead that you could just think, say 'I want to visit so-and-so', and a pocket-sized device, carried by you, would dutifully record that thought verbatim. It could also add tags, such as a category, much like a note-taking app.

This device wouldn't be limited by your writing speed or rate of speech. The barrier would lie not in the device, but in the user - the speed of their thought, the ultimate barrier.

Unfortunately, as of the time I am writing this, no such technology exists. The fastest way we can record our thoughts now is by speech recognition technology, since we speak faster than we type. The accuracy is improving steadily. However,unlike typing, speaking offers less in the way of privacy (barring subvocalization).

I like typing my thoughts out, especially on a pretty editor with a nice, monospaced font, such as VSCode with JetBrains Mono, which is my current setup. I type in Dvorak as there's more alternation between the left and right hands compared to QWERTY. There's something sublimely satisfying, seeing paragraphs of evenly spaced text fill a blank editor screen, with the squiggles of the autocorrect flashing now and then.

On some days, the rain and thunder might be pouring outside, while I fix and commit code, taking care to write each subroutine and function as elegantly as possible, with no unnecessary load on the computer. This strive towards perfection annoyed even myself initially, as I often got stuck on a particular feature for days. However, it soon began to feel sort of like a meditative process, almost Zen-like, where the goal was not in the resolution of the issue, but rather in the journey itself, and the numerous libraries I picked up along the way.

To me, coding is about building things and fixing those very same structures. Unlike in the real world, however, one can build anything imaginable in code. Any form of control or automation so desired is attainable, limited only by the laws of logic. Writing a program is like maintaining a garden.

The collaborative process in coding is unique to the field. We write programs to automate menial tasks. Later on, we release them to the public domain, where other people build larger programs on top of them, and in turn release them. This eventually culminates in large but polished libraries such as React and Django, or refinements to the languages themselves such as ES6. When you `import React from 'react'`, destructure a variable with `...` or `debounce` a function, you are calling upon the work of thousands of people who have developed these facilities, sometimes to solve the very same problem you are facing, and almost instantaneously. It is almost as if you are coding with the world at large.

## My Journey

I started out by reading books about computer hacking. Long ago, I borrowed a book on computer security (it was a thick book with a picture of a chessboard). I read about NMAP, TCP/IP, exploits on the IIS server (CodeRed), Windows LANMAN...though I didn't understand much then, I knew I really wanted to learn more about computers.

> "The programmer, like the poet, works only slightly removed from pure thought-stuff. He builds his castles in the air, from air, creating by exertion of the imagination. Few media of creation are so flexible, so easy to polish and rework, so readily capable of realizing grand conceptual structures." - Frederic P. Brooks

I was interested in computers and IT since I was in primary school. The web was in its infancy then; I still remember using 56kbps dialup.  Ironically, most of my interest came about when my parents locked my computer and I had to figure out ways of circumvention (booting Linux, keyloggers...). I learnt about networking from trying to configure the routers in my house mostly by trial and error - those IT people my parents called charged something north of $50 just for tweaking settings like DHCP or DNS and security. The 1999 movie 'The Matrix' was also a big inspiration to me.

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