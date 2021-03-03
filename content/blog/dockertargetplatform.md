Title: Making Dockerfiles architecture independent
Date: 2021-03-02 13:40
Category: DevOps
Tags: Docker, arm, amd64, multi-platform, Github actions, buildx, CI/CD, eLabFTW
Summary: Some pitfalls and tips for making Dockerfiles that build for any platform

## Introduction
I've been running a personal [eLabFTW](https://www.elabftw.net/) instance on the same server as this website for a while now, and wanted to get it running on a local instance for our whole research group.
The group leader had a spare QNAP TS-231P NAS lying around, so we chose this as our testbed.
When I installed it on my own VPS it was pretty easy, so I thought installing it on the NAS would be a job of a few minutes.
However, it turns out that eLabFTW is distributed via [Docker containers](https://www.docker.com/resources/what-container), and the application consists of the eLab container and a mysql container networked together and set up via [docker-compose](https://docs.docker.com/compose/).

## The problem with containers: CPU architecture
Docker containers are touted as platform independent and portable solutions to distribute software.
While Docker containers can indeed run on any OS, there is a catch: Docker containers are specific to the CPU architecture.
Most servers, computers, and laptops have CPUs with the amd64 or X86 architecture, which are all largely compatible and can run the same containers.
But small and embedded devices like phones, tablets, raspberry pi's and [recently the newest line of Apple Macbooks](https://www.apple.com/mac/m1/) use entirely different architectures based on designs by a company called ARM.
As it turned out, our NAS had an ARM processor, so I couldn't use the official eLabFTW images, which were built only for amd64 processors.
So I had to build my own image for this architecture.

## The Dockerfile and docker buildx
Luckily, I didn't have to start from scratch and could work off of [the Dockerfile created by the project maintainer](https://github.com/elabftw/elabimg).
To build images for a different architectures, I found the experimental `docker buildx` command as described in [this blogpost](https://www.docker.com/blog/multi-arch-images/).
So as a first try to build the image for ARM I did:

```bash
$ docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t nielscautaerts/elabimg:latest --push .
```

I was able to build the images for the different platforms without any apparent problems.
Full disclosure: I ran into a memory issue at first; make sure you give docker enough RAM when building big applications!
But when I tried to fire it up on the NAS it didn't work.
Pouring back over the Dockerfile I discovered where the problem was:

```
ENV S6_OVERLAY_VERSION 2.2.0.1

...

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-amd64.tar.gz /tmp/
RUN tar xzf /tmp/s6-overlay-amd64.tar.gz -C /
```

Something was being downloaded during the build process that was platform specific.
Looking [at the releases from that repo](https://github.com/just-containers/s6-overlay/releases) I found they luckily had builds for all the relevant architectures.
But how could I now alter the build process so that it would build on all platforms I wanted?

## Making the Dockerfile flexible with build-args
One solution would be just to create a separate docker file for each platform.
This wasn't an acceptable solution for me because of maintainability concerns.

Another solution I thought of was adding a build argument.
This way you can supply additional arguments to the `docker build` command that can be referred to inside the Dockerfile.
So I set up the build argument `ARCHITECTURE` and modified the Dockerfile as follows.


```
ARG ARCHITECTURE=amd64
ENV ARCHITECTURE $ARCHITECTURE

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${ARCHITECTURE}.tar.gz /tmp/
RUN tar xzf /tmp/s6-overlay-${ARCHITECTURE}.tar.gz -C /
```

Using this file, I could build the docker image for the right platform with separate commands, for example

```bash
$ docker buildx build --platform linux/arm/v7 -t --build-arg ARCHITECTURE=arm nielscautaerts/elabimg:latest --push .
```

When no build argument is passed in, `ARCHITECTURE` defaults to amd64.
This way the maintainer of eLabFTW wouldn't have to change anything about his CD workflow.
This was sufficient to solve my QNAP issue; I ended up with a valid eLabFTW image that worked on the arm/v7 architecture.

## A better solution using TARGETPLATFORM
There were still some problems with this method and I was looking for a more general solution.
What if I wanted to build the image for multiple platforms simultaneously?
Then I ran into a problem because if I supply `--platform linux/arm/v7,linux/amd64` to the `build` command, then I can not pass different `ARCHITECTURE` values to those builds.
I could run the `build` command separately for each platform of course, but then I would have to push all of the images to the container repository under a different tag, otherwise they would overwrite each other.
I didn't want images labeled `latest-amd64`, `latest-arm`, etc.; I wanted the tag `latest`. 
The platform should resolve automatically when the user calls `docker pull`.

Thanks to github user crazy-max ([see thread](https://github.com/docker/build-push-action/issues/309)) I learned that during the build process an additional argument is passed in automatically: `TARGETPLATFORM` ([see documentation](https://docs.docker.com/engine/reference/builder/#automatic-platform-args-in-the-global-scope)).
This can be called upon during the build process and be used to perform conditional logic.
I was finally able to resolve the issue by replacing the `ADD` and `RUN` commands in the snippets above with this hacky-looking bit:

```
ARG TARGETPLATFORM
RUN if [ "$TARGETPLATFORM" = "linux/amd64" ]; then ARCHITECTURE=amd64; elif [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then ARCHITECTURE=arm; elif [ "$TARGETPLATFORM" = "linux/arm64" ]; then ARCHITECTURE=aarch64; else ARCHITECTURE=amd64; fi \
    && curl -sS -L -O --output-dir /tmp/ --create-dirs "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${ARCHITECTURE}.tar.gz" \
    && tar xzf "/tmp/s6-overlay-${ARCHITECTURE}.tar.gz" -C /
```

Basically what happens in the code is I am testing for different values of the `TARGETPLATFORM` and setting a variable `ARCHITECTURE` based on the result.
This variable is then used to download the right `s6` version.
I had to replace the `ADD` function with `curl` because setting the `ARCHITECTURE` variable in one `RUN` command is not persistent to the next Docker command.
I had to do quite a bit of shell-script debugging to get rid of all the syntax errors, but in the end this snippet did the trick.
With this Dockerfile I didn't have to supply an additional `build-arg` and I could simultaneously build for different platforms using:
```
$ docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t nielscautaerts/elabimg:latest --push .
```

## From local to Github actions
I don't want to build these images on my laptop every time there is an update to eLabFTW.
Therefore, I formalized the build process in a [Github Actions](https://github.com/features/actions) workflow, which can be found [here](https://github.com/din14970/elab-arm-docker/blob/master/.github/workflows/makeimage.yaml) and also below for convenience.

```
name: Deploy images to Docker

on:
    push:
        branches: [ master ]

jobs:
    buildandpush:
        runs-on: ubuntu-latest
        env:
            S6V: 2.2.0.1
            DOCKER_FILE: Dockerfile
        steps:
            - name: Get latest release commit eLabFTW
              id: elabftw_version
              uses: abatilo/release-info-action@v1.3.0
              with:
                  owner: elabftw
                  repo: elabftw

            - name: Verify release commit elabftw
              env:
                  LATEST: ${{ steps.elabftw_version.outputs.latest_tag }}
                  LATEST_DATE: ${{ steps.elabftw_version.outputs.latest_tag_published_at }}
                  LATEST_COMMIT: ${{ steps.elabftw_version.outputs.target_commitish }}
              run: |
                  echo "eLabFTW: Version $LATEST was released $LATEST_DATE and has commit $LATEST_COMMIT"

            - name: Checkout elabimg repo
              uses: actions/checkout@v2
              with:
                  repository: "din14970/elabimg"
                  ref: "hypernext"

            # https://github.com/docker/setup-qemu-action#usage
            - name: Set up QEMU
              uses: docker/setup-qemu-action@v1

            # https://github.com/marketplace/actions/docker-setup-buildx
            - name: Set up Docker Buildx
              uses: docker/setup-buildx-action@v1

            # https://github.com/docker/login-action#docker-hub
            - name: Login to Docker Hub
              uses: docker/login-action@v1
              with:
                username: ${{ secrets.DOCKER_HUB_USERNAME }}
                password: ${{ secrets.DOCKER_HUB_TOKEN }}

            # see https://github.com/docker/build-push-action/issues/276
            - name: Set elab version branch
              run: echo "ELAB_BRANCH=hypernext" >> $GITHUB_ENV

            # https://github.com/docker/build-push-action#multi-platform-image
            - name: Build AMD64 and push to Docker Hub
              uses: docker/build-push-action@v2
              with:
                context: .
                file: ${{ env.DOCKER_FILE }}
                platforms: linux/amd64,linux/arm/v7,linux/arm64
                push: true
                build-args: |
                    S6_OVERLAY_VERSION=${{ env.S6V }}
                    ELABFTW_VERSION=${{ env.ELAB_BRANCH }}
                tags: |
                    ${{ secrets.DOCKER_HUB_USERNAME }}/${{ secrets.DOCKER_HUB_REPOSITORY }}:latest
                    ${{ secrets.DOCKER_HUB_USERNAME }}/${{ secrets.DOCKER_HUB_REPOSITORY }}:${{ steps.elabftw_version.outputs.latest_tag }}
```

The images are available [here](https://hub.docker.com/repository/docker/nielscautaerts/elabimg/tags?page=1&ordering=last_updated).
So if you are interested in running eLabFTW on your ARM NAS or even or a raspberry pi, this is now possible!

## Next steps
I'd like to create a bot that informs me when there is a new version of eLabFTW and automatically triggers a new build; I made a little prototype but it's not yet working.
I'm hoping to work with the maintainer to bring this workflow directly into the main eLabFTW repository so that official images for ARM will be supported soon.

## Conclusion
Docker images may be very portable but it is important to remember that they are CPU architecture dependent.
Building images for different architectures can get quite hacky.
If your Dockerfile is architecture independent then have a look at `buildx`.
Otherwise, I hope my experience described in this article gives you some ideas on possible workarounds.
