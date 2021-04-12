Title: Deploying a pelican static site with Github actions
Date: 2021-04-12 13:40
Category: DevOps
Tags: Github actions, CI/CD, website, pelican, ssh
Summary: Deploying this site to the server with Github Actions

I set up this site a while ago but was not entirely happy with how I was deploying the site.
As discussed [here]({filename}./thissitehowto.md), I build the site with `pelican content -s publishconf.py` and then manually copy the contents of the output folder into the right folder on the server.
I could have also set up a hook such that when the `pelican` command is run, the result is automatically copied.
This option I did not explore fully, because I also wanted to keep the site open source and have the "deployed version" of the site match the master branch of the Github repo.
So it seemed to make most sense to me that I set up a Github action that builds and updates my site whenever I push or merge with the master branch.
This post details the process.

## Underpriviledged account creation and access rights

Github needs SSH access to my server for it to securely copy files over.
I didn't feel comfortable copying the root SSH access key into the repo secrets so instead I created a new user on the server.

```
$ useradd -m -s /bin/bash github
```

The `-m` will create a `home` directory for the user and `-s` sets the default shell (why not bash right?).
I also gave the new user a password just in case

```
$ passwd github
```

I do not want this user to have root privileges, but it needs to have write access to the site folder in `/var/www/html/`.
By default, on Debian with nginx, the owner and group of these folders are both `www-data`.
So I added my new user to this group.

```
$ usermod -G www-data github
```

The folders do not by default give the group write permission.
To change this for the specific site:

```
$ chmod g+rw /var/www/html/sitefolder/
```

## SSH access and secrets

Then it is time to create an ssh key for this specific user; we run `ssh-keygen` for the specific user.
Github will get the private key so it can access the server via the user `github`

```
$ sudo -u github ssh-keygen
```

By just pressing enter the whole time (we don't want a password and we are ok with the default key name) we end up with two files in the folder `/home/github/.ssh`: `id_rsa` and `id_rsa.pub`.
We have to authorize the public key, we can do this simply by renaming the public key file.

```
$ mv /home/github/.ssh/id_rsa.pub /home/github/.ssh/authorized_keys
```

The private key must be accessible to Github actions, so I view the file with `cat` and copy the contents into a repository secret (repository page > Settings > Secrets) which we will call `SSHKEY`.
For good measure I also added a few more secrets to the repo, mainly as variables not because they are true secrets.

* `USER`: ssh user (in this case just github)
* `PORT`: ssh port number (by default this is 22, but can be changed to reduce bot activity in log files)
* `HOST`: the server adres

## The Github action

Finally in the site repo we create a file `.github/workflows/deploy.yml`.
Whenever we push to the master branch, this workflow should:

* check out the repo so it has access to the contents
* set up python and pip
* install pelican and the right plug-ins
* build the site
* connect via ssh and remove the contents from `/var/www/html/sitename`
* copy the built site into this folder

We achieve this with the following action, thanks to `appleboy`'s `scp-action` and `ssh-action`.

```yaml
name: deploy

on: 
    push:
        branches:
            - master

jobs:
    build:
        runs-on: ubuntu-latest

        steps:
        - uses: actions/checkout@v1

        - name: Set up Python 3.8
          uses: actions/setup-python@v2
          with:
            python-version: 3.8

        - name: Install pelican with markdown
          shell: bash
          run: "pip install invoke pelican[markdown]"

        - name: Set up pelican and dependencies
          shell: bash
          run: "pip install -r requirements.txt"

        - name: Build the project
          shell: bash
          run: "pelican content -s publishconf.py"

        - name: Check if we have everything
          shell: bash
          run: "ls -la output/"

        - name: Remove the existing file structure
          uses: appleboy/ssh-action@master
          with:
              host: ${{ secrets.HOST }}
              username: ${{ secrets.USER }}
              key: ${{ secrets.SSHKEY }}
              port: ${{ secrets.PORT }}
              script: |
                rm -rf /var/www/html/sitename/*

        - name: Copy output via scp
          uses: appleboy/scp-action@master
          with:
              host: ${{ secrets.HOST }}
              username: ${{ secrets.USER }}
              port: ${{ secrets.PORT }}
              key: ${{ secrets.SSHKEY }}
              source: "output/"
              target: "/var/www/html/sitename"

        - name: Copy output into site root
          uses: appleboy/ssh-action@master
          with:
              host: ${{ secrets.HOST }}
              username: ${{ secrets.USER }}
              key: ${{ secrets.SSHKEY }}
              port: ${{ secrets.PORT }}
              script: |
                mv /var/www/html/sitename/output/* /var/www/html/sitename/
                rmdir /var/www/html/sitename/output
```

The action could be shorter but it does the job.
For some reason `scp` kept copying the entire `output` folder into `/var/www/html/sitename` instead of just the contents, so the last step just moves those files into the right place.

## Conclusion

Now whenever I push to master or merge a pull request the site will be automatically rebuilt and deployed.
No more manual copying with FileZilla, the Github master branch will correspond to the ground truth.
The nice thing is also that now I could work on a development branch and only merge with master when and article is finished.
In addition, someone else could easily contribute an article or fix to the website via a pull request.
