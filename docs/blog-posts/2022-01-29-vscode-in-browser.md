# Running VSCode in the browser

Key requirements:
- access windows filesystem
- develop remotely
- arbitrarily access ports on remote machine

remote extensions - https://github.com/coder/code-server/issues/1315

ssh-agent windows https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement

ssh into wsl on windows - https://www.hanselman.com/blog/the-easy-way-how-to-ssh-into-bash-and-wsl2-on-windows-10-from-an-external-machine

develop on remote docker host https://code.visualstudio.com/remote/advancedcontainers/develop-remote-host#_connect-using-docker-contexts

The issue of trust on first use

# Alternatives

## Running code-server in docker
Code-server can be run in a container too, and even be created on-the-fly with a particular environment from within code-server itself. This could be used as a common development environment for many projects, e.g. with Python, NodeJS and so on. However, it would need additional configuration to work out of the box for projects with particular requirements (e.g. CUDA support, ffmpeg etc).

# Authentication
## Code Server
There's no way to deauthenticate a websocket stream or at least check authenticity without something like a timer, which would delay deauths unlike ssh where if the tunnel is broken, the connection is gone

Turns out nginx can't terminate websocket connections once they're established

# Logging in from new clients
SSH won't allow me to use this on new computers

# Remote - containers
You must SSH into WSL on windows for this to work (https://code.visualstudio.com/docs/remote/ssh#_known-limitations)

|                         | code-server                                  | VSCode Remote-SSH   |
|-------------------------|----------------------------------------------|---------------------|
| Security                | Less secure                                  | As secure as SSH is |
| IP Visibility           | Can be hidden behind Cloudflare              | Public              |
| Authentication          | Password or external server<br>(note issues) | SSH password or key |
| Client requirements     | Any browser                                  | SSH client          |
| Access host filesystem  | Yes                                          | Yes                 |
| Forward ports from host | Yes                                          | Yes                 |
| Full VSCode experience  | No remote Docker support                     | Yes                 |