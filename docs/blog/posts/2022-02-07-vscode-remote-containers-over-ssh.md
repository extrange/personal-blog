---
categories:
    - Programming
date: 2022-02-07
---

# VSCode Remote Containers over SSH

When working remotely with a laptop, sometimes we might want access to more CPU power, RAM or a GPU. [VSCode supports accessing a remote machine][vscode-ssh], and if [Docker][docker] is installed on the remote machine, you can even connect to remote [development containers][devcontainers]. This approach tremendously saves battery life since computation is done on the remote server.

<!-- more -->

## Requirements

-   **Working SSH connection**. If you prefer to use SSH with certificates, you can refer to my [post](2022-02-07-ssh-with-certificates.md).

-   (on Windows) [**Setup `bash` as the default SSH shell**][bash-as-default-shell]. `bash` needs to be the default SSH shell, otherwise development containers will [not work][bash-must-be-default-shell].

Once that is done, you can follow the [official guide][vscode-ssh].

You can now run [powerful transformer models][gpt-j] and more from your laptop!

## Why not `code-server`?

[`code-server`][code-server] is a fully browser-based implementation of VSCode, and offers nearly the same experience. Compared to SSH, all that is needed is a client with a browser, and there is no need for SSH certificates.

However, the [lack of support for VSCode Remote-Container and Remote-SSH extensions][code-server-remote-extensions][^proprietary-extensions] were a deal-breaker for me, since I primarily develop within [development containers][devcontainers][^devcontainers].

`code-server` can be run in a Docker container too, and addtional `code-server` containers can even be created on-the-fly from within code-server itself. However, the configuration to automatically forward the relevant ports is going to be complicated.

**Authentication Concerns**

`code-server` uses a websocket stream. While `nginx` can be setup to [require authentication][nginx-auth] before initiating the stream, there's no simple way to deauthenticate a websocket stream[^nginx] once its established, unlike SSH connections.

A comparison of features:

|                         | `code-server`                       | VSCode Remote-SSH                     |
| ----------------------- | ----------------------------------- | ------------------------------------- |
| Security                | Less secure[^http-security]         | As secure as SSH is                   |
| IP Visibility           | Can be hidden behind Cloudflare     | Public                                |
| Authentication          | Password or external server[^nginx] | SSH password, 2FA, key or certificate |
| Client requirements     | Any browser                         | SSH client                            |
| Access host filesystem  | Yes                                 | Yes                                   |
| Forward ports from host | Yes                                 | Yes                                   |
| Full VSCode experience  | No Remote-Containers support        | Yes                                   |
| Open Source             | Yes                                 | Extension is proprietary              |

[^proprietary-extensions]: Sadly, VSCode is [not as open](https://news.ycombinator.com/item?id=24047638) as I used to think.
[^devcontainers]: For the reasons I do this, see [this post](2021-11-17-developing-in-wsl-containers.md).
[^nginx]: While `nginx` can [proxy websocket connections](https://nginx.org/en/docs/http/websocket.html), it can't terminate them once established.
[^http-security]: Web applications have multiple vectors of attack, for example the [OWASP Top Ten](https://owasp.org/www-project-top-ten/).

[bash-as-default-shell]: https://www.hanselman.com/blog/the-easy-way-how-to-ssh-into-bash-and-wsl2-on-windows-10-from-an-external-machine
[bash-must-be-default-shell]: https://code.visualstudio.com/docs/remote/ssh#_known-limitations
[code-server-remote-extensions]: https://github.com/coder/code-server/issues/1315
[code-server]: https://github.com/coder/code-server
[devcontainers]: https://code.visualstudio.com/docs/remote/containers
[docker]: https://www.docker.com/
[gpt-j]: https://huggingface.co/EleutherAI/gpt-j-6B
[nginx-auth]: https://nginx.org/en/docs/http/ngx_http_auth_request_module.html
[vscode-ssh]: https://code.visualstudio.com/docs/remote/ssh
