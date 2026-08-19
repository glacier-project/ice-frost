# ICE
This project shapes the ICE laboratory [(ICE)](https://www.icelab.di.univr.it/) through **Frost** platform.

We developed each machine by extending the **FrostReactor** and we connected them through the **FrostLink**.

We developed a **Scheduler** reactor that reads a recipe from an yml file and parses it into **Frost Messages**. The recipe is composition of two files: the recipe containing the commands to be sent and the conditions that are the responses we would like to have before advancing with the next task.

The Scheduler acts as an OPC UA client which sends messages to the link and wait for answers.

## Building

Frost is consumed as a Lingua Franca package, vendored as a submodule under
`lf-packages/frost`. Clone with submodules:

```sh
git clone --recurse-submodules https://github.com/glacier-project/ice-frost.git
```

If you cloned before `v0.1.0`, the submodule moved from `frost/` to
`lf-packages/frost/` — resync it:

```sh
git submodule sync --recursive
git submodule update --init --recursive
```

Install the Python dependencies and build:

```sh
pip install -r requirements.txt
lfc src/Main.lf
python src-gen/Main/Main.py
```

## Dockerfile
To build the Docker image, run inside the directory:

```sh
docker build -t ice-frost-app .
docker run --rm -it --entrypoint /bin/bash ice-frost-app
```
