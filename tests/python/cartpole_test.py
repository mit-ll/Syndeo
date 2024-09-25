import time
from dataclasses import dataclass

import ray
import torch
import typer
from ray.rllib.algorithms.algorithm import Algorithm
from ray.rllib.algorithms.algorithm_config import AlgorithmConfig
from ray.rllib.algorithms.ppo import PPOConfig
from utils_test import custom_log_creator
from utils_test import ray_stats


@dataclass
class Config:
    """Configuration for the Cartpole experiment."""

    n_iterations: int = 2
    train_batch_size: int = 5000
    sgd_minibatch_size: int = 256
    num_sgd_iter: int = 30
    rollout_workers: int = 19
    eval_workers: int = 1
    framework: str = "torch"
    seeds: int = 1
    grad_clip: int = 40  # default is 40, which can cause nans


# Configurable parameters
USER_CONFIGS = [Config()]


def get_env_ids() -> list:
    """List of environment Ids to run.

    Returns:
        list: List of environments to run.
    """
    # Environments: https://gymnasium.farama.org/environments/classic_control/
    return ["CartPole-v1"]


def get_config(env_id: str, user_config: Config) -> AlgorithmConfig:
    """Setup a Ray configuration for running an experiment.

    Args:
        env_id (str): The environment Id to run.
        user_config (Config): The user defined configuration parameters.

    Returns:
        AlgorithmConfig: The Algorithm object for building.
    """
    # Create a training configuration
    ppo_config = PPOConfig()
    ppo_config = ppo_config.environment(env=env_id)
    ppo_config = ppo_config.resources(num_gpus=torch.cuda.device_count())
    ppo_config.grad_clip = user_config.grad_clip
    ppo_config.train_batch_size = user_config.train_batch_size
    ppo_config.sgd_minibatch_size = user_config.sgd_minibatch_size
    ppo_config.num_sgd_iter = user_config.num_sgd_iter
    ppo_config = ppo_config.rollouts(num_rollout_workers=user_config.rollout_workers)
    ppo_config = ppo_config.framework(user_config.framework)
    ppo_config = ppo_config.evaluation(
        evaluation_parallel_to_training=True,
        evaluation_interval=1,
        evaluation_num_workers=user_config.eval_workers,
    )
    ppo_config = ppo_config.debugging(log_level="WARN")
    ppo_config = ppo_config.training(
        model={
            "fcnet_hiddens": [64, 64],
            "fcnet_activation": "relu",
        }
    )

    return ppo_config


def run_train_eval(
    algorithm: Algorithm,
    algo_config: AlgorithmConfig,
    user_config: Config,
    env_id: str,
):
    """Perform a training and evaluation iteration.

    Args:
        algorithm (Algorithm): The Algorithm class to perform training with.
        algo_config (AlgorithmConfig): The original Algorithm configuration object.
        user_config (Config): The user configuration object.
        env_id (str): The environment Id.
    """
    # Train for N iterations
    for _ in range(user_config.n_iterations):
        # Use a try catch for failed training attempts
        try:
            result = algorithm.train()
        except Exception as e:
            print(f"Training failed on: {env_id}")
            print(e)
            break

    # algo.evaluate()
    algorithm.stop()


def main(address: str):
    # ray start
    context = ray.init(address=address)
    ray_stats(context)

    print("-" * 100)
    print("Python Script".center(100))
    print("-" * 100)

    # Register the environments to use
    env_ids = get_env_ids()

    try:
        for user_config in USER_CONFIGS:
            for env_id in env_ids:
                # Timer
                tic = time.time()

                algo_config = get_config(env_id, user_config)

                # Generate a trainer
                algo = algo_config.build(
                    logger_creator=custom_log_creator(
                        custom_path="save/",
                        custom_str=f"MLP_{env_id}",
                    )
                )

                # Run the training
                run_train_eval(
                    algorithm=algo,
                    algo_config=algo_config,
                    user_config=user_config,
                    env_id=env_id,
                )

                # Calculate run time
                toc = time.time()
                runtime = round(toc - tic)
                print("=" * 100)
                print(f"Environment: {env_id}")
                print(f"Run Time: {runtime} secs")
                print("RLLib running of cartpole completed successfully!")

        print("Successully executed test!")

    finally:
        ray.shutdown()


if __name__ == "__main__":
    typer.run(main)
