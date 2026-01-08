FROM quay.io/jupyterhub/singleuser:5

USER root

RUN apt-get update -y && apt-get install -y tzdata

USER jovyan

RUN conda install mamba -y && conda clean -afy
RUN mamba install nodejs=22 nano jupyterlab=4.3 jupyterlab_widgets jupyterlab-lsp=5.1 jupyter-lsp-python=2.2 nb_conda_kernels ipyvue ipyvuetify ipywidgets -y && mamba clean -ay
RUN npm install pyright@1.1.406
RUN pip install ipyvue==1.11.3 ipyvuetify==1.11.3

RUN conda create -n omnipy -y

# From https://stackoverflow.com/a/60148365
SHELL ["conda", "run", "--no-capture-output", "-n", "omnipy", "/bin/bash", "-c"]

RUN mamba install python=3.12 ipykernel ipywidgets git -y && mamba clean -ay
RUN pip cache purge
RUN pip install omnipy==0.22.0
RUN pip install itables
RUN pip install ipy

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN jupyter-labextension enable @jupyter-lsp/jupyterlab-lsp
RUN jupyter server extension enable jupyterlab_lsp
RUN jupyter server extension enable jupyter_lsp

RUN mkdir shared
RUN mkdir -p .jupyter/lab/user-settings/\@jupyter-lsp/jupyterlab-lsp
RUN mkdir -p .jupyter/lab/user-settings/\@jupyterlab/completer-extension
RUN mkdir -p .jupyter/lab/user-settings/\@jupyterlab/apputils-extension
RUN mkdir -p .jupyter/lab/user-settings/\@jupyterlab/notebook-extension
RUN mkdir -p /opt/conda/etc/jupyter/jupyter_notebook_config.d/

RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/completion.jupyterlab-settings -O .jupyter/lab/user-settings/\@jupyter-lsp/jupyterlab-lsp/completion.jupyterlab-settings
RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/manager.jupyterlab-settings -O .jupyter/lab/user-settings/\@jupyterlab/completer-extension/manager.jupyterlab-settings
RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/notification.jupyterlab-settings -O .jupyter/lab/user-settings/\@jupyterlab/apputils-extension/notification.jupyterlab-settings
RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/plugin.jupyterlab-settings -O .jupyter/lab/user-settings/\@jupyter-lsp/jupyterlab-lsp/plugin.jupyterlab-settings
RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/tracker.jupyterlab-settings -O .jupyter/lab/user-settings/\@jupyterlab/notebook-extension/tracker.jupyterlab-settings
RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/pyright.json -O /opt/conda/etc/jupyter/jupyter_notebook_config.d/pyright.json

RUN fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER && \
    fix-permissions /home/$NB_USER/.jupyter/lab/user-settings && \
    fix-permissions /opt/conda/etc/jupyter

WORKDIR $HOME

RUN cd work && ln -s ../shared && cd ..