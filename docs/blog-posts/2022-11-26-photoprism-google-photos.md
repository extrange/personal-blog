---
tags:
  - Programming
---

# Photoprism - A Google Photos Replacement

My Google Photos account ran out of storage recently (since 2021 June, Google has [stopped providing free storage for photos in High Quality][google-photos]), and I was looking for a self-hosted, open source replacement, with similar features to Google Photos (fast gallery view, facial recognition, object detection).

![](/static/images/2022-11-26/photoprism.jpg)

I found [PhotoPrism][photoprism], an open-source, self-hosted, web-based photo manager with features such as facial recognition, object tagging, automatic import and organization, and the ability to view photos with location information on a map. I was impressed, and deployed it on my [server][server].

You can try their demo [here][photoprism-demo]. To get started (via Docker Compose), see the guide [here][get-started].

PhotoPrism can also be installed on mobile devices as a [Progressive Web App][pwa], offering a near-native app experience.

![](/static/images/2022-11-26/pwa.jpg)

## Mobile Sync

Photoprism suggests using [PhotoSync][photosync], an app available on Android and iOS. However, the WebDAV sync feature, essential to work with PhotoPrism, is a [paid][photosync-paid] feature.

Fortunately, [FolderSync][foldersync], another Android app, offers WebDAV sync. In fact, it also offers sync over many protocols, such as SSH, Google Drive, SFTP, SMB and more. In addition, it is highly customizable, and you can set schedules, sync rules (e.g. only when charging), frequency, files to exclude and so on.

If you are using [FolderSync][foldersync], you can sync your phone's camera folder (sometimes called `DCIM`) to PhotoPrism's [`import` folder][photoprism-import], using [WebDAV sync][photoprism-webdav], which also triggers the PhotoPrism import process (which adds photos to your library and organizes them) automatically.

If you want the files on your phone to be deleted after syncing:

- In FolderSync, ensure that [**Move files to target folder**][move-files-target-folder] is checked, and [**Use temp-file scheme**][temp-file-scheme] is unchecked.
- In PhotoPrism under Library > Import, ensure **Move Files** is checked.

With these settings, whenever FolderSync syncs, photos in your phone are deleted and uploaded to PhotoPrism, freeing up space.

[google-photos]: https://support.google.com/photos/answer/10100180?hl=en
[photoprism]: https://photoprism.app/
[photoprism-demo]: https://try.photoprism.app/
[server]: 2022-05-22-my-self-hosting-journey.md
[get-started]: https://docs.photoprism.app/getting-started/docker-compose/
[photosync]: https://www.photosync-app.com/home.html
[photosync-paid]: https://play.google.com/store/apps/details?id=com.touchbyte.photosync.fullfeatured&hl=en&gl=US
[foldersync]: https://www.tacit.dk/foldersync
[photoprism-import]: https://docs.photoprism.app/user-guide/sync/webdav/#connect-to-a-webdav-server
[move-files-target-folder]: https://foldersync.io/docs/help/folderpairsettings/#advanced-one-way-sync-options
[temp-file-scheme]: https://foldersync.io/docs/help/folderpairsettings/#advanced
[photoprism-webdav]: https://docs.photoprism.app/user-guide/sync/webdav
[pwa]: https://docs.photoprism.app/user-guide/pwa/