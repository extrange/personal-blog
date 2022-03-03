---
tags:
  - Programming
---
# `npm update` does not write updated versions to `package.json`

Update: This issue has been fixed in `npm` [8.3.2](https://github.com/npm/cli/releases/tag/v8.3.2).

Found this out the hard way.

I was working on an app, and I wanted to update its dependencies.

```
> npm outdated
Package   Current  Wanted  Latest  Location               Depended by
date-fns   2.27.0  2.28.0  2.28.0  node_modules/date-fns  frontend
```

So I updated with `npm update`.

Then I had a look at `package.json` and to my surprise, `date-fns` wasn't updated:

```json
"dependencies": {
    "date-fns": "^2.27.0",
}
```

However, the actual package was updated:

```
> npm list
my-app@0.1.0 /workspaces/my-app
├── date-fns@2.28.0
```

After googling, I finally found that this was a [behavioral change](https://github.com/npm/cli/issues/2704) ever since `npm` v7.

As a workaround for now, I use [`npm-check-updates`](https://www.npmjs.com/package/npm-check-updates) to update version numbers in `package.json`.