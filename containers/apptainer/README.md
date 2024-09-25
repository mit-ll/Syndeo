# [Apptainer](https://apptainer.org)

## Description
* Primary method for building and maintaining **secure** containers.
* Used primarily in settings where root access is not possible.
* Deployable to any machine.

## Packages
The default development containers will these packages by default.  Only the essentials are included.

* [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)
* [Oh My Bash](https://github.com/ohmybash/oh-my-bash)

## Example
To get started with the included example:

```bash
apptainer build miniconda.sif miniconda.def
apptainer build base.sif base.def
```

## Build

```bash
apptainer build <container_id>.sif <container_id>.def # builds a .sif image from a .def file
```

## Shell
```bash
apptainer shell <container_id>.sif             # shelling into image
```

## Adding Writable Partition

This is the standard method for adding an overlay to an Apptainer image.
```bash
apptainer overlay create --size 1024 <container_id>.sif     # adds 1GB to image
```

You can use the Linux `dd` tool to create file storage files and then attach them Apptainer images.  The `dd` tool treats file storage volumes on Linux systems like independent files.  You provide `dd` with a input file `if=<file>` and an output file `of=<file>` with the batch size `bs` and counts to determine the total size.  The storage volume file is then attached to the Apptainer image.
```bash
dd if=/dev/zero of=overlay.img bs=1M count=1000 && mkfs.ext3 -d overlay overlay.img
sudo apptainer shell --overlay overlay.img <container_id>.sif
```

## Creating Instances

```bash
apptainer instance start <container_id>.sif <instance_id>       # create an instance
apptainer instance list                                         # show instances
apptainer exec instance://<instance_id> cat /etc/os-release     # exec on instance
apptainer shell instance://<instance_id>                        # shell into an instance
```
