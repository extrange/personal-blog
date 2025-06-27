---
date: 2025-06-27
categories:
  - Programming
---

# Migrating from Btrfs to ZFS

In my article on [self hosting], I initially wrote about how I was using Btrfs to store my data. However, I ran into issues with app database read/writes becoming very slow due to fragmentation. Additionally, I wanted better space efficiency than offered by RAID1 as I was expanding my hard drive collection.

<!-- more -->

I ran some [performance tests] to compare Btrfs and ZFS, and the results showed that ZFS with a `recordsize` of 128k was pretty resilient to fragmentation (simulated by random in-place writes into a file).

I finally decided on ZFS with RAIDZ2, for the following reasons:

- RAIDZ's space efficiency vs RAID1 in Btrfs
- Ability to tune the `recordsize` to reduce the impact of fragmentation
- RAIDZ2 lets me have up to 2 drives failing, avoiding the dangers of a second disk failing during the intensive resilvering happening during a RAIDZ1 rebuild

## Initial Data Migration

I wrote some scripts to move my filesystem on Btrfs to the ZFS

## Setup and Initial Data Migration

I started with the following:

- 12TB: Btrfs RAID1
- 12TB: Btrfs RAID1
- 8TB: Btrfs RAID1
- 14TB: Off site archive
- 14TB: Spare
- 10TB: Spare

Usable space: 16TB in RAID1 (max 1 drive failure)

Initially, I attempted to migrate my Btrfs snapshots to ZFS (via `rsync` with [scripts][btrfs-zfs-scripts]). However, I realized that this was extremely space inefficient: reflink-ed blocks in Btrfs would take up additional space, and turning on deduplication in ZFS is memory intensive, and cannot be fully disabled until all deduplicated data is rewritten.

??? note "Deduplication"

    I deliberated about whether to turn on deduplication. However, the space savings were miniscule:

    ```
    ❯ sudo zdb -S storage
    Simulated DDT histogram:

    bucket              allocated                       referenced
    ______   ______________________________   ______________________________
    refcnt   blocks   LSIZE   PSIZE   DSIZE   blocks   LSIZE   PSIZE   DSIZE
    ------   ------   -----   -----   -----   ------   -----   -----   -----
        1    33.2M   4.14T   4.07T   4.07T    33.2M   4.14T   4.07T   4.07T
        2     376K   46.5G   44.6G   44.6G     760K   94.0G   90.1G   90.1G
        4    1.85K    190M    125M    126M    8.31K    840M    541M    543M
        8      162   10.2M   2.73M   2.87M    1.66K    114M   27.7M   29.0M
        16       36   3.04M   1.29M   1.30M      853   74.6M   34.5M   34.9M
        32       24   2.76M   1.35M   1.35M      855   95.7M   45.0M     45M
        64        6     82K   77.5K     88K      480   6.25M   5.80M   6.58M
    128        3     41K   8.50K     12K      595   9.70M   1.76M   2.32M
    256        3      4K      4K     12K      892   1.18M   1.18M   3.48M
    Total    33.6M   4.19T   4.12T   4.12T    34.0M   4.24T   4.16T   4.16T

    dedup = 1.01, compress = 1.02, copies = 1.00, dedup * compress / copies = 1.03
    ```

So, I decided to `rsync` my Btrfs array to a ZFS dataset I created on the 10TB drive (you can see the rsync options I used [here][btrfs-zfs-scripts]).

??? note "ZFS Dataset Options"

    I created a pool with a child dataset, with the following properties:

    - `compression=zstd-3`
    - `atime=off`

!!! warning

    My data did not have any redundancy during the transfer to/from the 10TB drive. In fact, I encountered one checksum error on ZFS while reading back from the drive (fortunately, I had a backup of that file)

After that was done, I wanted to create a RAIDZ2 pool. However, I couldn't use one of the 14TB drives as that still had my old Btrfs archives on it. So, I created a RAIDZ2 pool using the [sparse file trick][sparse-expansion-zfs]:

- First, I created a 14TB sparse file with `truncate -S 14T sparse.tmp`
- Then, I created a RAIDZ2 zpool with the 2x12TB drives and 1 14TB drive, plus the sparse file
- I took the sparse file offline

I then started the transfer:

```sh
zfs send -cve storage/data@now | zfs receive -sv storage-raid/data
```

Finally, I added the second 14TB drive (after offloading my backups) and ran `zpool replace` to add it back to the array.

My final setup:

- 10TB off site archive
- 12TB raidz2
- 12TB raidz2
- 14TB raidz2
- 14TB raidz2

Usable space: 24TB in RAIDZ2 (max 2 drive failures)

## ZFS Limitations

ZFS is not without limitations. In particular:

- RAIDZ vdevs cannot be shrunk
- You cannot add a device which is smaller than the smallest disk in a RAIDZ vdev
- No rebalance after expanding RAIDZ vdev (data-to-parity ratio for old blocks is unchanged)
- Cannot convert a mirror to RAIDZ in-place
- Top-level vdevs can only be removed if the primary pool storage does not contain a top-level raidz vdev, all top-level vdevs have the same sector size, and the keys for all encrypted datasets are loaded.

Raidz expansion notes:

- Free space is [miscalculated]. However, this can be mitigated somewhat by [using sparse files and offlining them].

## Monitoring:

ZFS has nice utilities to monitor drive and pool status.

Of note, `zpool iostat` is really useful for identifying pre-failing drives and diagnosing poor performing arrays.

For example, with the following command, we can see the distribution of reads and writes in a pool, the slowest drives and more:

```sh
❯ zpool iostat -vly <pool> 5 1
                capacity     operations     bandwidth    total_wait     disk_wait    syncq_wait    asyncq_wait  scrub   trim  rebuild
pool          alloc   free   read  write   read  write   read  write   read  write   read  write   read  write   wait   wait   wait
------------  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----
storage-temp  1.27T  7.83T      0    161      0   148M      -   95ms      -   12ms      -    1us      -   82ms      -      -      -
  sde         1.27T  7.83T      0    161      0   148M      -   95ms      -   12ms      -    1us      -   82ms      -      -      -
------------  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----
```

More details [here].

[self hosting]: 2022-05-22-my-self-hosting-journey.md
[performance tests]: 2025-06-07-btrfs-zfs-performance.md
[btrfs-zfs-scripts]: https://github.com/extrange/btrfs-to-zfs
[sparse-expansion-zfs]: https://old.reddit.com/r/zfs/comments/1i7r7xj/create_a_raidz2_with_one_drive_offline/
[using sparse files and offlining them]: https://github.com/openzfs/zfs/discussions/15232#discussioncomment-6904427
[miscalculated]: https://github.com/openzfs/zfs/pull/12225
[here]: https://klarasystems.com/articles/openzfs-using-zpool-iostat-to-monitor-pool-perfomance-and-health/
