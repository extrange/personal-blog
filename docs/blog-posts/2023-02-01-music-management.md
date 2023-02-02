# Music Management with Navidrome, DSub and Beets

Previously on Windows, I was using [MediaMonkey][mediamonkey] to manage my music. It offered wireless syncing (over LAN) for the associated Android client, and worked well.

When I [switched to Linux][computing-philosophy], I had to look for a replacement. I wanted a solution that was free and open-source, could be self-hosted on a server, and supported features such as bookmarks, playlists and transcoding (for clients not supporting certain formats).

After considering [Airsonic][airsonic-advanced], [Funkwhale][funkwhale] and [Jellyfin][jellyfin], I settled upon [Navidrome][navidrome].

## [Navidrome][navidrome]

![](../static/images/2023-02-01/navidrome.jpg)

Navidrome is "an open source web-based music collection server and streamer", with support for on-the-fly transcoding[^issue] for devices which cannot play certain formats (e.g. FLAC). It is accessible via the web. It also has [Subsonic][subsonic] API support, which lets it work with the [large variety][subsonic-clients] of Subsonic clients available across platforms.

It also comes with a responsive, HTML5 web UI written as a progressive web app. Navidrome also keeps a record of play counts, recently played songs and also supports bookmarks, which is useful for audiobooks.

Additionally, multiple users can share a single server and maintain their own playlists.

## [DSub][dsub]

<figure>
  <div style="max-width: 300px"><img src="/static/images/2023-02-01/dsub.jpg" alt="DSUb" loading="lazy"/></div>
</figure>

DSub ([available on the F-Droid store][dsub]) is the best Subsonic Android client in my opinion. It is the only client I have found which supports all of:

- Playlist managment
- Caching of audio files for offline playback
- Bookmarks

I cache songs in my playlists, which lets me listen to them when I don't have internet access.

## [Beets][beets]

I use the [Beets][beets] CLI tool for tagging music and organizing. It supports fingerprinting audio files and looking up tag information from multiple sources.

I currently run Beets with several plugins in Docker.

[airsonic-advanced]: https://github.com/airsonic-advanced/airsonic-advanced
[issue]: https://github.com/navidrome/navidrome/issues/351
[mediamonkey]: https://www.mediamonkey.com/
[computing-philosophy]: 2022-02-27-my-computing-philosophy.md#stable-open-source-environment
[funkwhale]: https://funkwhale.audio/
[jellyfin]: https://jellyfin.org/
[navidrome]: https://www.navidrome.org/
[subsonic]: http://www.subsonic.org/pages/api.jsp
[subsonic-clients]: https://www.navidrome.org/docs/overview/#apps
[dsub]: https://f-droid.org/en/packages/github.daneren2005.dsub/
[beets]: https://beets.io/

[^issue]: Navidrome does not yet support per-format transcoding options (i.e. if you turn on transcoding for a client, Navidrome will transcode all files, irregardless of format, to the specified format. See this [issue][issue].