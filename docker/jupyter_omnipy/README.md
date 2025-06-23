## Build and push multi-platform Docker image on MacOS
### Install multipass
Follow installation instructions: https://canonical.com/multipass/install

### Setup Docker on multipass
Instructions: https://documentation.ubuntu.com/multipass/en/latest/how-to-guides/manage-instances/run-a-docker-container-in-multipass/#alias-of-the-docker-commands

Example:
```bash
multipass launch docker --name docker-dev --cpus 6 --memory 10G --disk 100G --bridged
```

Add to `~/.zshrc` (or `~/.bashrc`):
```
export PATH="$PATH:$HOME/Library/Application Support/multipass/bin"
```

- Setup QEMU and buildx inside docker VM:
```bash
multipass shell docker-dev
docker run --rm --privileged multiarch/qemu-user-static -
-reset -p yes
docker buildx create --name builder
docker buildx inspect --bootstrap
exit
```
- Log in to Docker Hub:
```bash
docker login
```
- Build the image:
```bash
cd docker/jupyter_omnipy
multipass transfer -r * docker-dev:
docker buildx build --platform linux/amd64,linux/arm64 -t fairtracks/jupyter_omnipy:0.xx.yy --push .
```

## Update JupyterLab installation on OpenStack
```bash
ssh -i .ssh/<rsa-file-name> alma@<openstack-ip>
sudo -s
su - jupyter
docker pull fairtracks/jupyter_omnipy:0.xx.yy
```
Edit `jupyterhub_config.py`:
```python
c.DockerSpawner.image = 'docker.io/fairtracks/jupyter_omnipy:0.xx.yy'
```
Restart JupyterHub:
```bash
killall jupyterhub
./run_all.sh
```
