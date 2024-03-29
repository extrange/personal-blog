---
categories:
    - Programming
date: 2022-05-21
---

# Note-Taking

Few of us could live life without jotting down our thoughts somewhere. Throughout the years we have developed some sort of note-taking system, either cobbled together slowly by ourselves, or something off the shelf.

I use electronic notes primarily as they are more accessible compared to paper notes and can be backed up easily.

Previously I used a Word document synced on Google Drive. However, this came with several limitations:

<!-- more -->

-   Formatting issues
-   Not editable over command-line e.g. with Vim
-   Not searchable unless opened
-   Inability to see backlinks (other notes which link to this note)
-   Limited categorization ability (only headings/subheadings possible)

I have since decided to move to **Markdown**, the main reasons being:

-   Open, widely adopted format (important for the future)
-   Can be edited in almost any application
-   Can be searched easily (e.g. with `grep`)
-   Can be linked to/from each other

![](../../static/images/2022-05-21/obsidian.jpg)

The choice of editor I am currently using at present is [Obsidian][obsidian]. In comparison with VSCode, [Obsidian][obsidian]:

-   Supports viewing backlinks natively
-   Updates links when notes are moved
-   Supports image/video drag and drop[^vscode-drag]

However, Obsidian is not [FOSS][foss], and for that reason, I avoid (as far as possible) using its non-standard Markdown syntax. At present I only use wikilinks and tags.

## Backup and Access

The folder with my notes is stored on my [server](2022-05-22-my-self-hosting-journey.md), which is itself in a RAID-1 configuration with backup.

[Foam][foam] is a great VSCode extension with backlink, graph view and other cool Markdown features which I host on the web with [code-server][code-server], allowing me to edit my notes anywhere.

I access my notes on my phone via the Obsidian Android app.

With my laptop, I access my notes with SSHFS.

Local access is over [nfs](2022-05-22-my-self-hosting-journey.md#storage-and-backup).

[foss]: https://en.wikipedia.org/wiki/Free_and_open-source_software
[code-server]: https://github.com/coder/code-server
[foam]: https://github.com/foambubble/foam
[obsidian]: https://obsidian.md/

[^vscode-drag]: VSCode generates incorrect links for images when connected to a remote host (all the generated links start with `remote://`)
