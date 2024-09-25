import datetime
import json
import os.path
import random
import re
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from os.path import exists

import typer
from rich import box
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from trogon import Trogon
from typer.main import get_group
from typing_extensions import Annotated


# Custom types
class ConfigType(str, Enum):
    """
    Refs:
        * https://github.com/Textualize/trogon/issues/69
    """

    container = "container"
    bare_metal = "bare_metal"

    def __str__(self):
        return str(self.value)


@dataclass
class Cfg:
    """Global configuration settings.  These should be changed based on local directory structure."""

    RAY_SLURM_DIR: str = ".ray_slurm"
    SRC_TEMPLATES: str = "src/templates"
    RESOURCES_FILE: str = f"{RAY_SLURM_DIR}/resources.json"
    CONFIG_HEAD: str = f"{RAY_SLURM_DIR}/head.json"
    CONFIG_CPU: str = f"{RAY_SLURM_DIR}/cpu.json"
    CONFIG_GPU: str = f"{RAY_SLURM_DIR}/gpu.json"
    CONFIG_MISC: str = f"{RAY_SLURM_DIR}/misc.json"
    SRC_TEMPLATE_HEAD: str = f"{SRC_TEMPLATES}/template_head.sh"
    SRC_TEMPLATE_CPU: str = f"{SRC_TEMPLATES}/template_cpu.sh"
    SRC_TEMPLATE_GPU: str = f"{SRC_TEMPLATES}/template_gpu.sh"
    DEST_TEMPLATE_HEAD: str = f"{RAY_SLURM_DIR}/template_head.sh"
    DEST_TEMPLATE_CPU: str = f"{RAY_SLURM_DIR}/template_cpu.sh"
    DEST_TEMPLATE_GPU: str = f"{RAY_SLURM_DIR}/template_gpu.sh"
    LOG_PATH: str = "logs"
    CONTAINER_TGT_PATH: str = "/tmp/ray_container.sif"  # default if no path is provided


# Tagging tools
curr_time = datetime.datetime.now().strftime("%-m-%-d-%y_%H:%M:%S")
userid = os.getenv("USER")

# Typer application CLI
console = Console()
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}, rich_markup_mode="markdown"
)


@app.command()
def tui(ctx: typer.Context):
    """
    🐤 Open the Graphic User Interface (GUI) for Syndeo.

    Refs:
        * https://github.com/Textualize/trogon/issues/10
    """
    Trogon(get_group(app), click_context=ctx).run()


@app.command(help=":mountain: **Create** a new Ray **head** config file.")
def setup_head(
    job_name: Annotated[str, typer.Option(help="name of the job")] = "ray_head_node",
    output: Annotated[str, typer.Option(help="output file name")] = f"ray_head_{curr_time}",
    cpus_per_task: Annotated[int, typer.Option(help="number of cpus set per task")] = 1,
    nodes: Annotated[int, typer.Option(help="number of nodes to assign to this job")] = 1,
    partition: Annotated[str, typer.Option(help="type of partition used")] = "normal",
    gres: Annotated[str, typer.Option(help="number of GPUs to allocate")] = "n/a",
    time: Annotated[str, typer.Option(help="run time days-hours:min:secs")] = "0-00:05:00",
    hostenv: Annotated[
        ConfigType,
        typer.Option(help="container|bare_metal (only accepts Singularity containers)"),
    ] = ConfigType.bare_metal,
    tmpdir: Annotated[
        str,
        typer.Option(help="temporary directory to write files to (host system)"),
    ] = "/tmp",
    container_src_path: Annotated[str, typer.Option(help="path of source container")] = "n/a",
    container_tgt_path: Annotated[
        str,
        typer.Option(help="the file system location of the node to copy container to"),
    ] = Cfg.CONTAINER_TGT_PATH,
):
    config = {key: value for key, value in locals().items() if key != "self"}
    setup_node(config, Cfg.CONFIG_HEAD)
    show_config()


@app.command(help=":large_orange_diamond: **Create** a new Ray **CPU** config file.")
def setup_cpu(
    job_name: Annotated[str, typer.Option(help="name of the job")] = "ray_cpu_workers",
    output: Annotated[str, typer.Option(help="output file name")] = f"ray_cpu_{curr_time}",
    cpus_per_task: Annotated[int, typer.Option(help="number of cpus set per task")] = 1,
    nodes: Annotated[int, typer.Option(help="number of nodes to assign to this job")] = 1,
    partition: Annotated[str, typer.Option(help="type of partition used")] = "normal",
    gres: Annotated[str, typer.Option(help="number of GPUs to allocate")] = "n/a",
    time: Annotated[str, typer.Option(help="run time days-hours:min:secs")] = "0-00:05:00",
    hostenv: Annotated[
        ConfigType,
        typer.Option(help="container|bare_metal (only accepts Singularity containers)"),
    ] = ConfigType.bare_metal,
    tmpdir: Annotated[
        str,
        typer.Option(help="temporary directory to write files to (host system)"),
    ] = "/tmp",
    container_src_path: Annotated[str, typer.Option(help="path of source container")] = "n/a",
    container_tgt_path: Annotated[
        str,
        typer.Option(help="the file system location of the node to copy container to"),
    ] = Cfg.CONTAINER_TGT_PATH,
):
    config = {key: value for key, value in locals().items() if key != "self"}
    setup_node(config, Cfg.CONFIG_CPU)
    show_config()


@app.command(help=":large_blue_diamond: **Create** a new Ray **GPU** config file.")
def setup_gpu(
    job_name: Annotated[str, typer.Option(help="name of the job")] = "ray_gpu_workers",
    output: Annotated[str, typer.Option(help="output file name")] = f"ray_gpu_{curr_time}",
    cpus_per_task: Annotated[int, typer.Option(help="number of cpus set per task")] = 1,
    nodes: Annotated[int, typer.Option(help="number of nodes to assign to this job")] = 1,
    partition: Annotated[str, typer.Option(help="type of partition used")] = "gaia",
    gres: Annotated[str, typer.Option(help="number of GPUs to allocate")] = "gpu:volta:2",
    time: Annotated[str, typer.Option(help="run time days-hours:min:secs")] = "0-00:05:00",
    hostenv: Annotated[
        ConfigType,
        typer.Option(help="container|bare_metal (only accepts Singularity containers)"),
    ] = ConfigType.bare_metal,
    tmpdir: Annotated[
        str,
        typer.Option(help="temporary directory to write files to (host system)"),
    ] = "/tmp",
    container_src_path: Annotated[str, typer.Option(help="path of source container")] = "n/a",
    container_tgt_path: Annotated[
        str,
        typer.Option(help="the file system location of the node to copy container to"),
    ] = Cfg.CONTAINER_TGT_PATH,
):
    config = {key: value for key, value in locals().items() if key != "self"}
    setup_node(config, Cfg.CONFIG_GPU)
    show_config()


def show_config():
    """Shows the configuration of the current Ray setup."""

    table = Table(title="Ray Cluster Configuration on SLURM", box=box.ROUNDED)

    table.add_column("Parameters", justify="right", style="bold")
    table.add_column("Head Node", justify="left")
    table.add_column("Worker Nodes - CPU", justify="left")
    table.add_column("Worker Nodes - GPU", justify="left")

    populate_row(Cfg.CONFIG_HEAD, Cfg.CONFIG_CPU, Cfg.CONFIG_GPU, table)

    console = Console()
    console.print(table)


@app.command(help=":zap: **Run** all **config** files.")
def run() -> dict:
    """Run the current configuration.

    Returns:
        dict: Information of the current run.
    """
    show()

    # Setup a random directory for the Ray IP directory
    runtime_dict = generate_runtime_data()

    # Display the Ray IP TMP directory for debugging purposes
    run_script(Cfg.SRC_TEMPLATE_HEAD, Cfg.DEST_TEMPLATE_HEAD, Cfg.CONFIG_HEAD, runtime_dict)
    run_script(Cfg.SRC_TEMPLATE_CPU, Cfg.DEST_TEMPLATE_CPU, Cfg.CONFIG_CPU, runtime_dict)
    run_script(Cfg.SRC_TEMPLATE_GPU, Cfg.DEST_TEMPLATE_GPU, Cfg.CONFIG_GPU, runtime_dict)

    info = get_run_info()
    info["ray_ip_dir"] = runtime_dict["ray_ip_dir"]

    return info


def generate_runtime_data() -> dict:
    """Generate a randomized temporary directory that is accessible by all worker nodes.  This must be a shared file directory.  This must be added to the config dictionaries so that at construction, the templates can all point to the same directory.

    Returns:
        dict: Information of the runtime.
    """

    runtime_dict = {}

    # Generate variables
    ray_ip_dir = "$HOME/tmp/" + random_id()

    # Add variables to config dict
    runtime_dict["ray_ip_dir"] = ray_ip_dir

    # Save misc data to file
    with open(Cfg.CONFIG_MISC, "w") as fp:
        json.dump(runtime_dict, fp)

    return runtime_dict


@app.command(help=":fire: **Delete** the **all** configs.")
def delete_all():
    """Deletes the current configuration."""
    delete_head()
    delete_cpu()
    delete_gpu()


@app.command(help=":fire: **Delete** the current **head** config.")
def delete_head():
    """Delete the head configuration."""
    if exists(Cfg.CONFIG_HEAD):
        os.remove(Cfg.CONFIG_HEAD)
    show_config()


@app.command(help=":fire: **Delete** the current **CPU** config.")
def delete_cpu():
    """Delete the CPU configuration."""
    if exists(Cfg.CONFIG_CPU):
        os.remove(Cfg.CONFIG_CPU)
    show_config()


@app.command(help=":fire: **Delete** the current **GPU** config.")
def delete_gpu():
    """Delete the GPU configuration."""
    if exists(Cfg.CONFIG_GPU):
        os.remove(Cfg.CONFIG_GPU)
    show_config()


@app.command(help=":white_check_mark: **Display** the current *config settings* file.")
def show():
    """Show the current configuration."""
    show_config()


def run_script(
    src_template_path: str,
    dest_template_path: str,
    config_path: str,
    runtime_dict: dict,
):
    """Launch the sbatch script for a certain configuration.

    Args:
        src_template_path (str): The source template file to replace with user values.
        dest_template_path (str): The destination template file with the user values inserted.
        config_path (str): Path to the user configuration files.
        runtime_dict (dict): Runtime dictionary of values generated at runtime.
    """
    # Return if configuration file has not been set
    if exists(config_path) is False:
        return

    # Read the config dict & add runtime data
    config_dict = json_read(config_path)
    master_dict = config_dict | runtime_dict  # merge two dicts

    # Generate full template with all fields filled out from a source template
    replace_text(master_dict, src_template_path, dest_template_path)

    # Execute sbatch
    results = subprocess.run(["sbatch", dest_template_path], capture_output=True, text=True)
    assert results.returncode == 0, f"Error Code: { results.returncode }, Info: {results}"

    # Read the logs to determine whether the nodes have been successfully created.
    # This may take a few mins depending on how many nodes the user has requested.
    # Thus, a progress bar is provided along with an estimated wait time.
    verify_nodes(master_dict)


def setup_node(config: dict, config_file_path: str):
    """Write a Head/CPU/GPU configuration file to json format.

    Args:
        config (dict): The configuration to save.
        config_file_path (str): Path to the save directory.
    """
    # Perform verification of the config dict
    verify_config(config)

    # Save the configuration file for this setup
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
    with open(config_file_path, "w") as fp:
        json.dump(config, fp)

    print(":party_popper: [green]Success!")


def verify_config(config: dict):
    """Verify the Head/CPU/GPU configuration is valid.

    Args:
        config (dict): Config dictionary.
    """
    key_names = [
        "job_name",
        "output",
        "cpus_per_task",
        "nodes",
        "partition",
        "gres",
        "time",
        "hostenv",
        "container_src_path",
        "container_tgt_path",
    ]

    # Check that all required names are found
    assert all([name in config for name in key_names]), "Missing name in config!"

    # Check that resource file exists (use to update the cpus for each partition)
    if os.path.exists(Cfg.RESOURCES_FILE):
        resources_dict = json_read(Cfg.RESOURCES_FILE)

        # Try reading the config if it exists
        try:
            config["cpus_per_task"] = resources_dict["cpus_per_task"][config["partition"]]
            print(f":information: resources file detected: {Cfg.RESOURCES_FILE}")
            print(f":information: updating cpus_per_task...")
        except KeyError:
            pass

    # Check that container path is valid
    if config["hostenv"] == ConfigType.container:
        # Checks
        check1 = config["container_src_path"] != "n/a"
        check2 = exists(os.path.expanduser(config["container_src_path"]))
        check3 = str(config["container_tgt_path"]).endswith(".sif")

        assert check1, "Must set container_src_path if using containers!"
        assert check2, "Container source file must exist!"
        assert check3, "Must specify .sif file path"


def get_run_info() -> dict:
    """Read the log file after starting the run.  Here we monitor the printout statements coming from the log file to get some key variables.

    Args:

    Returns:
        dict: Information dictionary.
    """

    info = {}

    # Extracting info from logs
    print(Panel("[bold]Head Config"))
    if os.path.isfile(Cfg.CONFIG_HEAD):
        head_dict = json_read(Cfg.CONFIG_HEAD)
        head_log = head_dict["output"]

        head_file = open(f"{Cfg.LOG_PATH}/{head_log}.log")
        lines = head_file.readlines()

        # Strips the newline character
        for line in lines:
            check1 = "HEAD Node ID" in line
            check2 = "HEAD Node IP" in line
            check3 = "HEAD Node Address" in line

            # Populate info dict
            key_val = re.split("=|\n", line)[-2].strip()  # format for ip address

            if check1:
                info["head_id"] = key_val
            if check2:
                info["head_ip"] = key_val
            if check3:
                info["head_addr"] = key_val

    # Print to console
    print_run_table(info)

    return info


def verify_nodes(master_dict: dict):
    """Read the logs generated by the scheduler to verify that runtime executed successfully.

    Args:
        master_dict (dict): Master dictionary that holds both user defined variables and runtime variables.
    """
    # Get log path (remove the previous logging if it exists!)
    log_path = f"{Cfg.LOG_PATH}/{master_dict['output']}.log"
    if exists(log_path):
        os.remove(log_path)

    # Wait for log file to be created
    while exists(log_path) is False:
        time.sleep(0.25)

    active_nodes = 0
    requested_nodes = master_dict["nodes"]
    requested_parition = master_dict["partition"]

    with Progress() as progress:
        task = progress.add_task("Registering Nodes...", total=requested_nodes)

        while active_nodes < requested_nodes:
            with open(log_path) as f:
                content = f.read()

            active_nodes = content.count("Ray runtime started")
            progress.update(task, completed=active_nodes)
            time.sleep(0.25)

    console.print(
        f":party_popper: Successfully started #{requested_nodes} on {requested_parition} partition"
    )
    console.print(f"logs can be found at: {log_path}")


def print_run_table(info: dict):
    """Create a CLI table for displaying information.

    Args:
        info (dict): Information to be displayed.
    """
    # Print to console
    table = Table(title="Ray Setup")
    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Values", justify="left", style="green")

    for key, val in info.items():
        table.add_row(key, val)

    console = Console()
    console.print(table)


def replace_text(replacements: dict, src: str, dest: str):
    """Replace text in a document with values specified in a dictionary.

    Args:
        replacements (dict): Replacement values to insert into document.
        src (str): Path of the original template.
        dest (str): Path of the destination copy template with replacements.
    """
    with open(src) as infile, open(dest, "w") as outfile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace("{" + src.upper() + "}", str(target))
            outfile.write(line)


def random_id(length: int = 3) -> str:
    """Random Id generator for temporary Ray addresses.

    Args:
        length (int, optional): Length of the random folder. Defaults to 3.

    Returns:
        str: Unique identifier.
    """
    alpha_num = "0123456789abcdefghijklmnopqrstuvwxyz"
    id = ""
    for _ in range(0, length, 1):
        id += random.choice(alpha_num)
    return id


def populate_row(
    head_json: str,
    worker_cpu_json: str,
    worker_gpu_json: str,
    table: Table,
):
    """Prints a rich table row based on information from a json.

    Args:
        head_json (str): Path to json file.
        worker_cpu_json (str): Path to json file.
        worker_gpu_json (str): Path to json file.
        table (Table): Rich table.
    """

    row_names: dict = {
        "Job Name": [],
        "Output File": [],
        "CPU/Task": [],
        "Nodes": [],
        "Partition": [],
        "GPUs": [],
        "Time Limit": [],
        "HostEnv": [],
        "TmpDir": [],
        "Container Source": [],
        "Container Target": [],
    }

    # Iterate over all json files
    for config_path in [head_json, worker_cpu_json, worker_gpu_json]:
        # Populate
        if os.path.isfile(config_path) is False:
            for name in row_names.keys():
                row_names[name].append(None)  # populate with null values
        else:
            # Load the configuration json file
            config = json_read(config_path)

            # Print out the row values from the config path
            for name, val in zip(row_names.keys(), config.values()):
                row_names[name].append(str(val))  # populate with real values

    # Print rows
    for name in row_names.keys():
        table.add_row(name, *row_names[name])


def json_read(filename: str) -> dict:
    """Reads data from a json file.

    Args:
        filename (str): File to read.

    Returns:
        dict: Json data converted into dictionary.
    """
    if exists(filename) is False:
        return {}

    with open(filename) as f_in:
        data = json.load(f_in)
        return data


if __name__ == "__main__":
    app()
