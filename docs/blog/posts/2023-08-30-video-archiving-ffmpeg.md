---
categories:
    - Programming
date: 2023-08-30
---

# Video Archiving with FFmpeg

I keep most of my photos and videos on [Photoprism](2022-11-26-photoprism-google-photos.md), a great open-source Google Photos alternative with features like facial recognition and viewing photos by location.

I also have a cheap action camera, the [Apeman Trawo A100][apeman], which supports recording video at 4K 50fps. However, the generated files are extremely large (with bitrates of 50,000kbps, so 1min of video is around ~500MB).

I needed a solution to compress my video files as much as possible, while still preserving (most) of the quality.

## AV1

Luckily, there exists the [AV1][av1] video codec, which is [supported][av1-support] by Chrome desktop/mobile and Firefox (at the time of this writing). The AV1 codec is advertised as the open (and royalty-free) equivalent of the [H.265][h265] codec, a proprietary codec designed as the successor to the H.264 (AVC) codec which is used widely.

AV1 is at least as good, and as fast, or even faster, than H.265 (and therefore H.264). For example, compared to [x265][x265][^x265] , [SVT-AV1][svt-av1][^svt-av1] is [better or equivalent][av1-benchmark] (as measured by [VMAF][vmaf], a new video quality benchmark from Netflix).

## FFmpeg

[FFmpeg][ffmpeg] is a popular, open source suite of libraries and programs for working with multimedia files. FFmpeg supports encoding AV1 via several encoders: `libaom` (the reference encoder), SVT-AV1 and `rav1e`. [SVT-AV1 `1.7.0`][svt-1.7.0] improves encoding speed by up to 50% for several presets, and as of the time of this writing, it is probably the best encoder to use.

To use `ffmpeg` to transcode by videos, I use the following command:

```bash
ffmpeg -i input-file -c:a copy -c:v libsvtav1 -crf 47 -preset 6 -vf scale=out_range=pc -map_metadata 0 output-file
```

Explanation of parameters:

-   `crf 47`: This sets the [quality level][crf] for each frame, with lower values indicating higher quality and larger file size. The default is 50.
-   `preset 8`: Presets control how many [efficiency features][presets] are used during the encoding process, with lower presets using more features and being smaller but slower. Presets range from 0 - 12, and the default is 8. Home enthusiasts generally use values between 4 - 6.
-   `vf scale=out_range=pc`: The Apeman A100 uses the [`yuvj420`][yuvj] pixel format, which is [deprecated][scaling], resulting in washed out contrast when playing on a non-aware video player (e.g. VLC). This fixes that issue.
-   `map_metadata 0`: Some encoders store video metadata such as `creation_time`, and this preserves it in the output.

## Results

After using the parameters above, my library of 4K videos was compressed from 24GB to 3.7GB (a 15x reduction).

[^x265]: A popular open source H.265 encoder.
[^svt-av1]: An open source AV1 encoder.

[apeman]: https://thetechnologyman.com/apeman-trawo-a100-action-camera-review-4k-50-fps-vs-gopro/
[av1]: https://en.wikipedia.org/wiki/AV1
[av1-support]: https://caniuse.com/av1
[h265]: https://en.wikipedia.org/wiki/High_Efficiency_Video_Coding
[av1-benchmark]: https://medium.com/@ewoutterhoeven/av1-is-ready-for-prime-time-svt-av1-beats-x265-and-libvpx-in-quality-bitrate-and-speed-31c1960703db
[vmaf]: https://scribe.rip/netflix-techblog/toward-a-practical-perceptual-video-quality-metric-653f208b9652
[x265]: https://en.wikipedia.org/wiki/X265
[SVT-AV1]: https://gitlab.com/AOMediaCodec/SVT-AV1
[ffmpeg]: https://ffmpeg.org/
[ffmpeg-av1]: https://trac.ffmpeg.org/wiki/Encode/AV1
[svt-1.7.0]: https://gitlab.com/AOMediaCodec/SVT-AV1/-/releases/v1.7.0
[crf]: https://trac.ffmpeg.org/wiki/Encode/AV1#CRF
[scaling]: http://trac.ffmpeg.org/wiki/Scaling
[yuvj]: https://trac.ffmpeg.org/ticket/225
[presets]: https://gitlab.com/AOMediaCodec/SVT-AV1/-/blob/master/Docs/CommonQuestions.md#what-presets-do
