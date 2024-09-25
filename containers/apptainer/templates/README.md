# 🦉 Overview
Singularity containers inherits your username and permissions from the host system.  The container allows you to install software in a controlled environment making it possible to **build once, deploy anywhere**.

To setup a container we need to: (1) create a definition file, (2) build an image, and (3) setup an overlay.  This will result in a Singularity container that has persistent storage allowing a developer to build software.

# Guide
## User Elevation
To build a container you will need sudo privileges.

```console
$ sudo su -
```

## Builds
We start by building an image file from a definition file.

```console
$ singularity build <name>.sif <name>.def
```

## Running
To run an image use the following command:

```console
$ singularity shell <name>.sif
```

If you want a writable space with your container execute:

```console
$ singularity shell --tmp-sandbox --userns --writable <name>.sif
```

## Tests
The built in tests included building (1) mamba image, (2) miniconda image, and (3) a base image.  The base image is likely your starting point for any project as it will include miniconda with Ubuntu 22.04 and the ability to add any additional conda environments of your choosing.

```console
python tests/build_test.sh
python tests/overlay_test.py
```

## Sandboxing
Sandboxing is a method for editing/building your image before packing into a SIF file.  While in sandbox mode, your changes persist.

```console
$ singularity build --sandbox <name>.sif
```

## Overlays
It is possible to embed an overlay image into the SIF file that holds a container. This adds writable persistent storage to your image.

To add a 1 GiB writable overlay partition to an existing SIF image:

```console
$ singularity overlay create --size 1024 <name>.sif
```

# Advance Concepts

## Dockerfile -> Singularity Image
In order to convert a Dockerfile into a Singularity image file the order of operations is: (1) build a docker image from Dockerfile, (2) build a Singularity image from the Docker image.

```console
$ docker build -t local/<my_container>:latest .

$ sudo singularity build <my_container>.sif docker-daemon://local/<my_container>:latest
```

An example can be found under `tests/convert_test.sh`.  To execute the test:
```console
$ bash tests/convert_test.sh
```

## Activating Anaconda
There are two properties that each shell has:

* it is either a **login** or a **non-login shell**
* and as well as an **interactive** or **non-interactive shell**.

A thorough explanation can be found [here](https://geniac.readthedocs.io/en/latest/conda.html).

When activating an Anaconda environment you are normally in a login and interactive terminal.  When you are working in the definition file of Singularity (i.e. %post), you are in a non-login terminal.  This means that some some of the processes the normally happen for a login terminal do not get applied when working with Singularity.

The way to fix this is by applying the log properties to your Singularity container via:

```console
$ conda create -n myenv python=3.10   # create a custom environment

$ . /opt/miniconda3/etc/profile.d/conda.sh   # activate login properties to terminal

$ conda activate myenv    # activating your custom environment
```

## Running Singularity on SLURM
Instructions for setting up Singularity to run on SLURM are found [here](https://nfdi4ing.pages.rwth-aachen.de/knowledge-base/how-tos/all_articles/how_to_run_a_job_on_the_cluster_using_slurm_and_singularity/).  In general, each Singularity image needs to be able to execute on its own.  The SLURM scheduler will dispatch the Singularity images to each node and proceed to run.



## Manually Building Writable Partitions
You can use tools like `dd` and `mkfs.ext3` to create and format an empty `ext3` file system image, which holds all changes made in your container within a single file. Using an overlay image file makes it easy to transport your modifications as a single additional file alongside the original `SIF` container image.

This script will create an overlay with 1GB of storage which can be attached to a Singularity
image.

```console
$ dd if=/dev/zero of=overlay.img bs=1M count=1000 && \
    mkfs.ext3 -d overlay overlay.img
```

Then attach the overlay with your image to create a writable container.

```console
$ sudo singularity shell --overlay overlay.img <name>.sif
```

## Persistent Overlays
A persistent overlay is a directory or file system image that “sits on top” of your immutable SIF container. When you install new software or create and modify files the overlay will store the changes.

If you want to use a SIF container as though it were writable, you can create a directory, an ext3 file system image, or embed an ext3 file system image in SIF to use as a persistent overlay. Then you can specify that you want to use the directory or image as an overlay at runtime with the `--overlay` option, or `--writable` if you want to use the overlay embedded in SIF.

If you want to make changes to the image, but do not want them to persist, use the `--writable-tmpfs` option. This stores all changes in an in-memory temporary filesystem which is discarded as soon as the container finishes executing.

You can use persistent overlays with the following commands:

```console
run
exec
shell
instance.start
```

Here is an example of applying a `.sif` overlay on top of an existing `img`.

```console
$ sudo singularity shell --overlay overlay.img <dev>.sif
```
