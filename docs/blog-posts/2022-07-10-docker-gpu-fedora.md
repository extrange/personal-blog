---
tags:
    - Programming
---

# Docker Containers with GPU access in Fedora

This guide will let you use a NVIDIA GPU in a Docker container (e.g. for Tensorflow/Pytorch).

Prerequisites:

-   Docker must be installed.
-   You have a NVIDIA GPU.

## 1. Install NVIDIA drivers from the RPM Fusion repository[^rpmfusion]:

```
sudo dnf install xorg-x11-drv-nvidia-cuda
```

It is necessary to reboot the system, as this package includes a [script](https://github.com/rpmfusion/xorg-x11-drv-nvidia/blob/master/xorg-x11-drv-nvidia.spec) which blacklists the default Nouveau drivers.

## 2. Add the [NVIDIA Container Runtime Repository](https://github.com/nvidia/nvidia-container-runtime)[^nvidia-repo]:

```
curl -s -L https://nvidia.github.io/libnvidia-container/centos7/libnvidia-container.repo | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
```

## 3. Install the NVIDIA Container Toolkit

This includes the NVIDIA Container Runtime, which adds a custom pre-start hook to all containers to allow GPU access):

```
sudo dnf install nvidia-container-toolkit
```

## 4. Register the runtime with Docker:

```
sudo tee /etc/docker/daemon.json <<EOF
{
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF
```

Tell `dockerd` to reload configuration:

```
sudo pkill -SIGHUP dockerd
```

_(Optional)_ To make all containers use the NVIDIA runtime by default, add the following to `/etc/docker/daemon.json`:

```
"default-runtime": "nvidia"
```

## 5. Finally, test GPU access in Docker with either:

```
docker run --runtime=nvidia --rm nvidia/cuda:10.2-base nvidia-smi
```

or

```
docker run --runtime=nvidia --gpus all --rm nvcr.io/nvidia/k8s/cuda-sample:nbody nbody -benchmark -numbodies=512000
```

And that's it!

**Note on VSCode**

If you are using VSCode [Remote Containers][remote-containers], you will need to add

```
"runArgs": ["--gpus","all"]
```

to your `devcontainer.json`. For some reason, `--runtime=nvidia` does not work.

[^rpmfusion]: Enable the RPM Fusion repositories in Fedora [here.](https://docs.fedoraproject.org/en-US/quick-docs/setup_rpmfusion/#proc_enabling-the-rpmfusion-repositories-using-command-line-utilities_enabling-the-rpmfusion-repositories)
[^nvidia-repo]: While there is no official Fedora support for `nvidia-container-runtime`, the Centos 7 repository [seems to work](https://github.com/NVIDIA/nvidia-docker/issues/553#issuecomment-381075335).

[remote-containers]: https://code.visualstudio.com/docs/remote/containers
