# Setup SSH with Certificates on Windows (and a bit of Linux)

The [Secure Shell Protocol][ssh] (SSH) allows one to remotely access a terminal interface on a remote machine. In addition, it allows for capabilities such as port tunneling[^port-tunneling], file transfers and screen forwarding.

The main reasons for setting up SSH access on my machine were to allow me to:

- Access the filesystem remotely and transfer files
- [Develop on VSCode remotely, in Remote-Containers][vscode-remote-containers]
- Tunnel ports to/from the remote machine (e.g., to access local applications only listening on `localhost`)

## SSH Authentication Methods

SSH supports [several authentication methods][ssh-auth], but the most common are:

- `password`: Login using the password of the host user. Most common, but vulnerable to password guessing attacks such as brute-force or dictionary-based methods.
- `publickey`: Utilizes [public key][public-key] authentication. Effectively resistant[^ssh-key-comparison] to any form of password guessing attack. This mode also allows for the use of **certificates**, and is the mode we will be using.

## Certificates

*What are certificates?*

Public key (aka asymmetric) encryption consists of a pair of keys - the *private* and *public* key. Any information encrypted with the public key can only be decrypted by the corresponding private key (and vice-versa). Public keys are shared publicly as the name suggests, while the private key is kept secret.

This can be used to create a [digital signature][digital-signature], an electronic variant of the handwritten signature, with similar properties:

- **Authentication**: Proves that a message was sent by the signer and no one else.
- **Non-repudiation**: Someone who has signed a message, cannot later deny they have done so.

In addition, a digital signature offers another property which handwritten signatures lack:

- **Integrity**: Any alteration to the signed message renders the signature invalid.

This brings us to the topic of certificates ([public key certificates][public-key-certificates]). These are electronic documents which prove that the owner's public key has been verified by some authority (the certificate issuer). This lets us trust the public keys of unknown entities, provided we trust the certificate issuer. In fact, this is how website certificates are issued under [TLS][tls], the cryptographic protocol powering HTTPS.

*SSH Certificates*

SSH certificates are essentially public SSH keys signed by some authority's private key, and allow the host to authenticate clients. When a client tries to connect to an SSH host, the client proves its identity by showing the host its public key certificate, which is signed by an authority the host trusts. Unlike [TLS][tls] however, there are no authorities trusted by default (aka [root certificate authorities][root-ca]). The trusted certificate authority on the host must be set by the user.

An advantage of using certificates is that all clients with public keys signed by an authority trusted by the host are automatically granted access, and there is no need to add or maintain the client's public keys in the [`authorized_keys`][authorized-keys] file on the host.

## 1. Setting up SSH on the host

First, ensure that OpenSSH, the open-source implementation of the [SSH][ssh] protocol and its tools, [is installed][install-openssh].

To check that `sshd`, the SSH daemon, is running on the host, open a Powershell terminal as an administrator and execute `Get-Service sshd`. The output should be similar to the following:

```terminal
Status   Name               DisplayName
------   ----               -----------
Running  sshd               OpenSSH SSH Server
```

Next, we will use [`ssh-keygen`][ssh-keygen] to  generate our server's public-private key pair, which will be used to sign the public keys of clients we want to allow SSH access from. *This keypair is different from the host's keypair (the keypair presented to clients), which is usually stored in `%ProgramData%\ssh\sshd_config`.*

Open a terminal and type the following:

```
ssh-keygen -f user_ca -t ed25519
```

- `-f`: the name of the keypair
- `-t`: the key algorithm, in this case [EdDSA with Curve25519][ed25519]

The passphrase is used to encrypt the private key, and is optional. You should get the following output:

```
Generating public/private ed25519 key pair.
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in user_ca.
Your public key has been saved in user_ca.pub.
The key fingerprint is:
SHA256:OxXXnTRmRiD7bxGMgyuU4fz4JTxKcEpGrngbIWpz/ow nick@Desktop-Nick
The key's randomart image is:
+--[ED25519 256]--+
|       . . . .oB |
|      o o o +.B.o|
|   . . = *.o.o.+.|
|  . o = = +oo . .|
| + o + .S+.* o . |
|. + . o .o+ + . .|
|   . .  o. .   o |
|    +    .    .  |
|   E o           |
+----[SHA256]-----+
```

`user_ca` contains the **private key** of this pair, and must be kept secret. 

Now, we need to tell our host to trust this public key, and enable public key authentication.

Open up `C:\ProgramData\ssh\sshd_config` and make the following changes:

- Set `PubkeyAuthentication` to `yes`
- Set `TrustedUserCAKeys` to the location of the `user_ca.pub` file generated above (note, use the full path to eliminate ambiguity)
- (optional but recommended) Disable password authentication: set `PasswordAuthentication` to `no`

Now, the host is ready to accept connections from clients whose public keys were signed by this private key (`user_ca` above).

## 2. Signing a client's SSH public key

We'll now sign a client's public key, using [`ssh-keygen`][ssh-keygen]. To make things a bit simpler, we'll generate the client's keypair on the host, sign it, and then return the signed keypair to the client.

First, we generate a keypair on the host: 

`ssh-keygen -f client_key -t ed25519`

Next, we use [`ssh-keygen`][ssh-keygen] to **sign** the client's public key (`client_key.pub`), with the private key of the keypair we generated earlier (`user_ca`). (Note: if you have added the private key to `ssh-agent`, see [below](#optional-adding-the-private-key-and-signed-public-key-to-ssh-agent).

`ssh-keygen -s user_ca -I <client_name> -n <usernames> -V +1d client_key.pub`

If you get an error about the public key not being found, use the absolute path to the `user_ca.pub` file instead, or ensure you run the command from the same directory as the `user_ca.pub` file.

- [`-s`][-s]: Indicates we want to sign a public key, with the provided private key.
- [`-I`][-I]: Key identifier, usually the name of the client. Will appear in logs.
- [`-n`][-n]: Comma-separated list of usernames (on the host, **not** WSL) which the client is allowed to log into the host as. Usernames must already exist on the host. Also known as 'principals'. If this option is omitted, the client will not be able to login.
- [`-V`][-V]: Validity interval of the certificate. If omitted, the certificate will be valid forever.

Then, copy the files `client_key` (private key), `client_key.pub` (public key) and `client_key-cert.pub` (signed public key) to the client [^linux-key-permissions]. Usually, these files are placed in `%UserProfile%\.ssh`.

## 3. Login

Now, test the SSH login from the client!

`ssh -i <PATH_TO_KEYFILE> you@your.domain.name`

where `<PATH_TO_KEYFILE>` is the location to the private key, e.g. `~\.ssh\client_key`.

You should not be prompted for a password.

If you don't want to keep having to specify the keyfile, create/edit the [config][ssh-config] file (usually at `~/.ssh/config`)[^openssh-config-windows]: 

```
Host ssh.your-domain.com
  HostName ssh.your-domain.com
  User your-username
  IdentityFile ~/.ssh/your_private_key
```

## (Optional) Adding the private key and signed public key to `ssh-agent`

[`ssh-agent`][ssh-agent] is a program which is able to store private keys and the signed public key using the appropriate secure credential storage for the operating system. This presents a more secure alternative than storing the private key unencrypted on the server.

In order to add keys to the agent, use [`ssh-add`][ssh-add]:

`ssh-add <keyfile>`

`<keyfile>` is the location of the private key, e.g. `user_ca`.


To check the keys which have been added to the agent, run `ssh-add -l`.

From now on, `ssh-agent` will automatically supply the signed public key and private key in commands such as `ssh`.[^ssh-add-windows]


(Only on Windows) 
Note: (On the host) If you added the host's certificate signing private key (e.g. `user_ca`) to `ssh-agent`, when you want to sign a client`s public key, you need to use the following command instead:

`ssh-keygen -Us user_ca -I <client_name> -n <usernames> -V +1d client_key.pub`

[`-U`][-U] indicates the private key should be extracted from `ssh-agent`.

## (Optional) Host Public Key Verification over DNS

How does the client authenticate the host the first time round? How does the client know that the public key the host is presenting really is the correct key, and not an attacker's key?

One way would be to verify the host's key fingerprint manually when connecting the first time. This is known as [trust on first use][tofu].

```
# ssh server@server.com
The authenticity of host 'server@server.com (192.168.65.2)' can't be established.
ECDSA key fingerprint is SHA256:e3eMAe6IrkZkWfCnYasBJUNRyHDC8SzDI0gLP9wWf1A.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

However, it's not easy to remember.

A better way is to add the host key to the DNS record, in a special type of record called [SSHFP][sshfp].

We can get the required information to add via `ssh-keygen`:

```
C:\WINDOWS\system32>ssh-keygen -r your.domain.name
your.domain.name IN SSHFP 4 1 3e35102ba1ef8777b74d257edcef0d6391cb9c19
your.domain.name IN SSHFP 4 2 f9212b988c5cb2e9027746b13339c6b32d9f1c49183620765476ba76b51ddd31
```

You need to add this information as an `SSHFP` record via your DNS registrar.

Finally, on the client, when we connect, we use the following command (non case-sensitive):

`ssh -o "VerifyHostKeyDNS ask" you@your.domain.name`

```
The authenticity of host 'your.domain.name (xx.xx.xx.xx)' can't be established.
ED25519 key fingerprint is SHA256:+SErmIxcsukCd0axMznGsy2fHEkYNiB2VHa6drUd3TE.
Matching host key fingerprint found in DNS.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Sadly, [**the OpenSSH client in Windows does not support `VerifyHostKeyDNS`**][verifyhostkeydns].

## Why not host your own SSH-CA?

Prior to my decision to use `ssh-keygen` as the certificate authority, I considered a number of alternative self-hosted SSH certificate authorities, but rejected them as follows:

- [Bastillion][bastillion] - Not certificate based. Also, need to manually upload and download the public keys and configure SSH.
- [Cloudflare Tunnel][cloudflare-tunnel-ssh] - Need to download on both server and client. I had some issues setting up SSH certificate login.
- [Step][step] - Need to download on both server and client. Also, TLS connection to `step-ca` from a client requires adding its generated root certificate as a trusted certificate[^leaf-certificates].
- [Teleport][Teleport] - Need to download on both server and client. Teleport Nodes (the server component) are not supported on Windows. The ability to record SSH sessions might be useful if I were to move to Linux.
- [Vault by HashiCorp][vault] - Need to download on both server and client.

Instead, to streamline the process of generating client certificates, I plan to write a certificate provisioning server which will probably rely on the (already-existing) 2FA login my web app backend uses. This would call `ssh-keygen` and return the signed public/private key pair.

[^port-tunneling]: You could use this to bypass firewalls, by running a [SOCKS proxy](https://ma.ttias.be/socks-proxy-linux-ssh-bypass-content-filters/) over the tunnel.
[^ssh-key-comparison]: RSA, EdDSA and Ed25519 are [considered secure](https://goteleport.com/blog/comparing-ssh-keys/). DSA (and ECDSA, which uses DSA in a different mathematical group, namely elliptic curves) are susceptible to [key recovery attacks](https://blog.trailofbits.com/2020/06/11/ecdsa-handle-with-care/) when the nonce is reused/predictable.
[^leaf-certificates]: This is because publicly trusted CAs only issue [leaf certificates](https://github.com/smallstep/certificates/discussions/466), which cannot be used to sign other certificates.
[^linux-key-permissions]: On Linux, the private key must have `chmod 600` permissions (i.e. no read access to anyone other than the user), otherwise `ssh-add` will refuse to add the key.
[^openssh-config-windows]: Unfortunately, Windows [does not generate](https://superuser.com/questions/1537763/location-of-openssh-configuration-file-on-windows) the `config` file automatically on connecting to a host, unlike Linux. You'll have to create it yourself.
[^ssh-add-windows]: On Windows, you may now safely delete the private key and the signed public key, as it is stored encrypted in the [registry](https://github.com/PowerShell/Win32-OpenSSH/issues/1487).


[-I]: https://man.openbsd.org/ssh-keygen.1#I
[-n]: https://man.openbsd.org/ssh-keygen.1#n
[-s]: https://man.openbsd.org/ssh-keygen.1#s
[-U]: https://man.openbsd.org/ssh-keygen.1#U
[-V]: https://man.openbsd.org/ssh-keygen.1#V
[authorized-keys]: https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement#deploying-the-public-key
[bastillion]: https://www.bastillion.io/
[cloudflare-tunnel-ssh]: https://developers.cloudflare.com/cloudflare-one/tutorials/ssh
[digital-signature]: https://en.wikipedia.org/wiki/Digital_signature
[ed25519]: https://en.wikipedia.org/wiki/EdDSA
[install-openssh]: https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse
[public-key-certificates]: https://en.wikipedia.org/wiki/Public_key_certificate
[public-key]: https://en.wikipedia.org/wiki/Public-key_cryptography
[root-ca]: https://en.wikipedia.org/wiki/Certificate_authority
[ssh-add]: https://man.openbsd.org/ssh-add.1
[ssh-agent]: https://man.openbsd.org/ssh-agent.1
[ssh-auth]: https://datatracker.ietf.org/doc/html/rfc4252#section-5
[ssh-config]: https://linux.die.net/man/5/ssh_config
[ssh-keygen]: https://man.openbsd.org/ssh-keygen.1
[ssh]: https://www.ssh.com/academy/ssh/protocol
[sshfp]: https://en.wikipedia.org/wiki/SSHFP_record
[step]: https://smallstep.com/docs/step-ca
[teleport]: https://goteleport.com/docs/getting-started/
[tls]: https://en.wikipedia.org/wiki/Transport_Layer_Security
[tofu]: https://en.wikipedia.org/wiki/Trust_on_first_use
[vault]: https://www.vaultproject.io/
[verifyhostkeydns]: https://github.com/PowerShell/Win32-OpenSSH/issues/1841
[vscode-remote-containers]: 2022-02-07-vscode-remote-containers-over-ssh.md

*[nonce]: Number Only used oNCE