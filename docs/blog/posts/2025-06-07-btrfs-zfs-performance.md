---
date: 2025-06-07
categories:
  - Programming
---

# Btrfs vs ZFS Performance

I have been using Btrfs for my server for a few years, but recently ran into performance issues with databases and snapshots. On the internet, ZFS seemed a pretty popular alternative, so I decided to compare the two in various aspects.

<!-- more -->

Both ZFS and Btrfs are [copy-on-write] (CoW) filesystems. These types of filesystems do not overwrite data in-place. Instead, they write file data to a new block, then update file metadata to point to it. As a result, their performance characteristics differ quite a bit from a traditional non-CoW filesystem like XFS or ext4.

For this article, I am using [test scripts] I have written which use [fio], a highly customizable I/O testing tool supporting a variety of testing patterns.

The test setup for this article is a spare hard drive I have:

```sh
❯ sudo parted /dev/sda print
Model: ATA TOSHIBA DT01ACA1 (scsi)
Disk /dev/sda: 1000GB
Sector size (logical/physical): 512B/4096B
```

All tests are done without caches/buffers (`direct=1` in fio).

ZFS supports some tunable parameters, some of which are:

- [recordsize]: This is the minimum size which must be read from either disk/cache when data in a file is to be modified. Writes which are smaller than this will require that the whole record be read and rewritten. Only applicable for datasets.
- [volblocksize]: The analogous property to recordsize, only applicable for volumes.
- [ashift]: The block alignment size that ZFS will use per vdev, or equivalently, the smallest possible IO on a vdev.
- [primarycache]: The Adaptive Replacement Cache, an improvement over LRU caches.

## Test Results

### Raw disk vs CoW filesystems

First, let's compare the performance of the raw disk versus these filesystems on top.

- Btrfs mount options: `datacow,noatime,defaults`
- ZFS dataset parameters: `atime=off, ashift=0, primarycache=metadata, compression=off`

Sequential:

| Test (in MB/s)   | Raw | Btrfs | ZFS 128k | ZFS 4k |
| ---------------- | --: | ----: | -------: | -----: |
| SEQ1M_Q8T1 Read  | 164 |   185 |      126 |     55 |
| SEQ1M_Q8T1 Write | 188 |   194 |      162 |     63 |
| SEQ1M_Q1T1 Read  | 190 |   194 |      153 |     69 |
| SEQ1M_Q1T1 Write | 188 |   184 |      143 |     64 |

Btrfs is the fastest here, while ZFS is the slowest. This might be due to read-ahead or other optimizations that Btrfs is doing that I'm not aware of.

Random:

| Test (in IOPS)    | Raw | Btrfs | ZFS 128k | ZFS 4k |
| ----------------- | --: | ----: | -------: | -----: |
| RND4K_Q32T1 Read  | 220 |   226 |      118 |    119 |
| RND4K_Q32T1 Write | 396 | 16977 |      116 |   8787 |
| RND4K_Q1T1 Read   | 140 |   147 |      109 |    121 |
| RND4K_Q1T1 Write  | 410 |  6139 |      112 |   8262 |

Btrfs wins again, with ZFS at 4k recordsize second.

On CoW filesystems, random writes with high queue depths can exceed that of the raw disk, since the writes can happen sequentially on disk. The filesystem maps them to the correct offsets in the file.

### Btrfs `datacow` vs `nodatacow`

We can directly evaluate the performance characteristics of Btrfs when CoW is turned off ([btrfs-admin]), and writes are done in-place.

| Test (MB/s)      | `datacow` | `nodatacow` | Raw |
| ---------------- | --------: | ----------: | --: |
| SEQ1M_Q8T1 Read  |       185 |         195 | 164 |
| SEQ1M_Q8T1 Write |       194 |         187 | 188 |
| SEQ1M_Q1T1 Read  |       194 |         195 | 190 |
| SEQ1M_Q1T1 Write |       184 |         195 | 188 |

No measurable difference in sequential performance.

| Test (IOPS)       | `datacow` | `nodatacow` | Raw |
| ----------------- | --------: | ----------: | --: |
| RND4K_Q32T1 Read  |       226 |         217 | 220 |
| RND4K_Q32T1 Write |     16977 |         402 | 396 |
| RND4K_Q1T1 Read   |       147 |         155 | 140 |
| RND4K_Q1T1 Write  |      6139 |         350 | 410 |

`nodatacow` random write speeds drop back to that of the raw disk.

As COW is turned off, random writes happen in-place on disk, and so suffer the same penalties as the raw disk.

!!! warning "nodatacow and checksums"

    When `nodatacow` is turned on, checksums (and compression) are disabled. Data corruption cannot be detected. In a RAID1 setup, it will not be possible to determine which disk has the correct block and correction is thus not possible.

    For this reason, despite the performance benefit, `nodatacow` should not be used.

    - Reddit: [NoDataCow and data loss]
    - Unraid: [Reconsider Btrfs NOCOW Default Option on domains Share due to Irrecoverable Corruption Risks][unraid-btrfs-nocow]

### In-place writes

A common database workload involves reading/writing repeatedly to the same file at random locations. This causes fragmentation of the file in CoW filesystems, since the writes are not done in-place. Subsequent sequential reading of the file is going to be slower, possibly close to that of random read performance.

We can simulate this by first writing a large file, doing random writes for a while, and then reading the same file sequentially.

- _ZFS dataset parameters: `atime=off, ashift=0, primarycache=metadata, compression=off`_
- _`datacow` and `nodatacow` refer to Btrfs with the respective mount option_

| Test                         | `datacow` | ZFS 128k | ZFS 4k | `nodatacow` |
| ---------------------------- | --------: | -------: | -----: | ----------: |
| SEQ1M_Q8T1 Write, MB/s       |       188 |      182 |     65 |         187 |
| SEQ1M_Q8T1 Read, IOPS (Pre)  |       187 |      183 |     82 |         192 |
| RND4K_Q32T1 Write, IOPS      |     20024 |       92 |   4933 |         271 |
| SEQ1M_Q8T1 Read, MB/s (Post) |         1 |       73 |      3 |         188 |

Here, we see that the performance of Btrfs with CoW is abyssmal.

At a recordsize of 128k, ZFS does much better, coming in at around half the perfomance if one were to write in-place (simulated via `nodatacow`). However at 4k recordsize, the performance drops significantly.

In fragmented files/workloads causing fragmentation, a large recordsize can help with sequential reads, at the price of slower random writes ([IO amplification due to read-modify-write cycles][recordsize-zfs-reddit]).

_Note: Btrfs does not offer any way to set the default extent size (the equivalent of recordsize). At present the minimum size is 4kB, with no limit on the maximum._

### Snapshot Performance

Taking repeated snapshots of a filesystem can affect performance, since defragmentation of any sort can't really happen while snapshotted blocks are still being referenced.

In this test, we take repeated snapshots (~3/s) while the random writes are being done, which should theoretically hamper optimization attempts to sequentially align data.

- ZFS dataset parameters: `atime=off, ashift=0, primarycache=metadata, compression=off`

| Test                         | 128k | 128k, snaps |  4k | 4k, snaps |
| ---------------------------- | ---: | ----------: | --: | --------: |
| SEQ1M_Q8T1 Write, MB/s       |  182 |         180 |  73 |        73 |
| SEQ1M_Q8T1 Read, MB/s (Post) |   73 |          90 |   7 |        10 |

### Btrfs `autodefrag`

Btrfs` [autodefrag][btrfs-admin] feature reads _"When enabled, small random writes into files (in a range of tens of kilobytes, currently it’s 64KiB) are detected and queued up for the defragmentation process."_

Let's see how turning this on changes things:

- Btrfs mount options: `datacow,noatime,defaults`

| Test                   | noautodefrag | autodefrag |
| ---------------------- | -----------: | ---------: |
| SEQ1M_Q8T1 Write       |     188 MB/s |   186 MB/s |
| SEQ1M_Q8T1 Read (Pre)  |     187 MB/s |   187 MB/s |
| RND4K_Q32T1 Write      |   20024 IOPS | 19708 IOPS |
| SEQ1M_Q8T1 Read (Post) |       1 MB/s |     1 MB/s |

No measurable difference.

### ZFS datasets vs volumes

ZFS also supports volumes (zvols), which are datasets that represent a block device. These can be passed as a raw disk to a VM, while still retaining checksums and the ability to snapshot the volume.

- _ZFS dataset parameters: `atime=off, ashift=0, primarycache=metadata, compression=off`_
- _ZFS zvol parameters: `ashift=12, compression=off`_
- _Despite turning off caches, results for the SEQ1M_Q8T1 read for zvols were unrealistically high and so they are omitted._

| Test (MB/s)      | Dataset, 16k | zvol, 16k |
| ---------------- | -----------: | --------: |
| SEQ1M_Q8T1 Write |          158 |       113 |
| SEQ1M_Q1T1 Read  |          156 |       264 |
| SEQ1M_Q1T1 Write |          151 |        43 |

| Test (IOPS)       | Dataset, 16k | zvol, 16k |
| ----------------- | -----------: | --------: |
| RND4K_Q32T1 Read  |          127 |       458 |
| RND4K_Q32T1 Write |          121 |       176 |
| RND4K_Q1T1 Read   |          112 |       210 |
| RND4K_Q1T1 Write  |          124 |        63 |

### RAID1/RAIDZ

We would also like to see if there are any performance gains when using a RAID1 setup, because in theory, reads can be fulfilled by both devices simultaneously.

To do this, we can run benchmarks on both Btrfs and ZFS, with and without RAID1 setup.

_In progress_

Of note when using RAIDZ, to improve random IOPS, [use less disks per vdev][raidz-iops] (or better, a mirror).

## Conclusion

CoW filesystems allow for efficient snapshotting, and come with a variety of useful features such as checksumming, compression and encryption (only for ZFS). The main drawbacks are due to the CoW mechanism, most clearly observed with heavy random write workloads which cause fragmentation. To some extent, this can be mitigated by increasing the extent/record size, sacrificing random write IOPS for sequential read speeds. At the time of this writing, only ZFS allows for that.

[copy-on-write]: https://wiki.archlinux.org/title/Btrfs#Copy-on-Write_(CoW)
[test scripts]: https://github.com/extrange/fio-benchmarks/
[fio]: https://github.com/axboe/fio
[btrfs-admin]: https://btrfs.readthedocs.io/en/latest/Administration.html
[NoDataCow and data loss]: https://old.reddit.com/r/btrfs/comments/xki69r/nodatacow_and_data_loss/
[unraid-btrfs-nocow]: https://forums.unraid.net/topic/123037-reconsider-btrfs-nocow-default-option-on-domains-share-due-to-irrecoverable-corruption-risks/
[volblocksize]: https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#zvol-volblocksize
[recordsize]: https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#dataset-recordsize
[ashift]: https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#alignment-shift-ashift
[primarycache]: https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#adaptive-replacement-cache
[raidz-iops]: https://web.archive.org/web/20150203051453/https://blog.delphix.com/matt/2014/06/06/zfs-stripe-width/
[recordsize-zfs-reddit]: https://old.reddit.com/r/zfs/comments/shnms0/plex_performance_sqlite_page_size_4k_align_to_zfs/hv4d0yp/
