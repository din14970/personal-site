Title: Making Dockerfiles architecture independent
Date: 2021-02-02 13:40
Category: DevOps
Tags: Docker, arm, amd64, Github, CI/CD, eLabFTW
Summary: Some pitfalls and tips for making Dockerfiles that build for any platform

Recently I wanted to install an electronic lab notebook application called [eLabFTW](https://www.elabftw.net/) on a QNAP TS-231P NAS.
I've been running a personal eLabFTW instance on this server for a while now and wanted to get it running for our group at the institute.
When I installed it for my server it was pretty easy, so I thought this would be a job of a few minutes.
Turns out that [eLabFTW] is distributed via [Docker containers](https://www.docker.com/resources/what-container), and the application consists of the eLab container and a mysql container networked together and set up via [docker-compose](https://docs.docker.com/compose/).
Docker containers are touted as platform independent and portable solutions to distributing software.
While Docker containers can indeed run on any OS, there is a catch: Docker containers are specific to the CPU architecture.
Most servers, computers, and laptops have CPUs with the amd64 or X86 architecture, which are all largely compatible.
But small and embedded devices like phones, tablets, raspberry pi's and [recently the newest line of Apple Macbooks](https://www.apple.com/mac/m1/) use entirely different architectures designed by ARM.
As it turned out, our NAS had an ARM processor, so I couldn't use the official eLabFTW image which was only built for amd64 processors.
So I had to build my own image for this architecture.

Luckily, I didn't have to start from scratch and could work off of [the Dockerfile created by the project maintainer](https://github.com/elabftw/elabimg).
To build images for a different architectures, I found the experimental `docker buildx` command as described in [this blogpost](https://www.docker.com/blog/multi-arch-images/).
So as a first try, on my Mac I did:

```bash
$ docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t nielscautaerts/elabimg:latest --push .
```

I was able to build the images for the different platforms (ok I ran into a memory issue first, make sure you give docker enough RAM to work with when building big applications)!
I fired it up on the NAS and ... it didn't work.
Pouring back over the Dockerfile I discovered where the problem likely was:

```
ENV S6_OVERLAY_VERSION 2.2.0.1

...

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-amd64.tar.gz /tmp/
RUN tar xzf /tmp/s6-overlay-amd64.tar.gz -C /
```

Something was being downloaded during the build process that was platform specific.
Looking [at the releases from that repo](https://github.com/just-containers/s6-overlay/releases) I found they luckily had builds for all the relevant architectures.
But how could I now alter the build process so that it would build on all platforms I wanted?

One solution would be just to create a separate docker file for each platform.
This wasn't an acceptable solution for me because the only difference was two lines.
This would be very difficult to maintain if changes would have to be made to the build process, and I suspected the maintainer of eLabFTW would not be very happy with that.

A first solution I thought of was adding a build argument.
This way you can supply additional arguments that can be used in the Dockerfile from the `docker build` command.
So I set up the build argument `ARCHITECTURE` and modified the Dockerfile as follows.


```
ARG ARCHITECTURE=amd64
ENV ARCHITECTURE $ARCHITECTURE

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${ARCHITECTURE}.tar.gz /tmp/
RUN tar xzf /tmp/s6-overlay-${ARCHITECTURE}.tar.gz -C /
```

This way I could build the docker image for the right platform with separate commands, for example

```bash
$ docker buildx build --platform linux/arm/v7 -t --build-arg ARCHITECTURE=arm nielscautaerts/elabimg:latest --push .
```

This was sufficient to solve my QNAP issue, I ended up with an eLabFTW image that worked on the arm/v7 architecture and could spin up the application.
The `ARCHITECTURE=amd64` sets the default architecture to `amd64` so the maintainer's CD pipelines would not be disturbed if he merged this change.

However, I was looking for a more general solution.
What if I wanted to build the image for multiple platforms simultaneously?
Then I ran into a problem because if I supply for example `--platform linux/arm/v7,linux/amd64` to the `build` command, then I can not pass different `ARCHITECTURE` values to those builds.
I could run the `build` command separately for each platform of course, but then the problem is that I have to push all of them to the container repository under a different tag, otherwise they would overwrite eachother.
I didn't want images labeled `latest-amd64`, `latest-arm`, etc., I just wanted `latest` and the platform to resolve automatically when the user calls `docker pull`.

Thanks to github user crazy-max ([see thread](https://github.com/docker/build-push-action/issues/309)) I learned that during the build process an additional argument is passed in automatically: `TARGETPLATFORM` ([see documentation](https://docs.docker.com/engine/reference/builder/#automatic-platform-args-in-the-global-scope)).
This can be called upon during the build process and be used to perform conditional logic.
I was finally able to resolve the issue by replacing the previous `ADD` and `RUN` commands with this hacky bit:

```
ARG TARGETPLATFORM
RUN if [ "$TARGETPLATFORM" = "linux/amd64" ]; then ARCHITECTURE=amd64; elif [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then ARCHITECTURE=arm; elif [ "$TARGETPLATFORM" = "linux/arm64" ]; then ARCHITECTURE=aarch64; else ARCHITECTURE=amd64; fi \
    && curl -sS -L -O --output-dir /tmp/ --create-dirs "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${ARCHITECTURE}.tar.gz" \
    && tar xzf "/tmp/s6-overlay-${ARCHITECTURE}.tar.gz" -C /
```

Basically I am testing for different values of the `TARGETPLATFORM` and setting a variable `ARCHITECTURE` based on this in order to download the right `s6` version.
I had to replace the `ADD` function with `curl` because setting the `ARCHITECTURE` variable in one `RUN` command is not persistent to the next Docker command.
As you can imagine, I had to do quite a bit of shell-script debugging to get rid of all the syntax errors, but in the end this did the trick.
Now I didn't have to supply an additional `build-arg` and I could use the same Dockerfile to build for all the platforms I wanted.
To do so, I could just call

```
$ docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t nielscautaerts/elabimg:latest --push .
```

I also didn't want this to run on my computer every time there was an update to eLabFTW, so instead I formalized this in a [Github Actions](https://github.com/features/actions) workflow, which can be found [here](https://github.com/din14970/elab-arm-docker/blob/master/.github/workflows/makeimage.yaml) and also below for convenience.

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

The next step would be to create a bot that informs me when there is a new version of eLabFTW and automatically creates a new build; I made a little prototype but it's not yet working.
I'm hoping to work with the maintainer to bring this workflow directly into the main repository so that official images for ARM will be supported soon.
