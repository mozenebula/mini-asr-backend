# ==============================================================================
# Copyright (C) 2024 Evil0ctal
#
# This file is part of the Whisper-Speech-to-Text-API project.
# Github: https://github.com/Evil0ctal/Whisper-Speech-to-Text-API
#
# This project is licensed under the Apache License 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
#                                     ,
#              ,-.       _,---._ __  / \
#             /  )    .-'       `./ /   \
#            (  (   ,'            `/    /|
#             \  `-"             \'\   / |
#              `.              ,  \ \ /  |
#               /`.          ,'-`----Y   |
#              (            ;        |   '
#              |  ,-.    ,-'         |  /
#              |  | (   |  Evil0ctal | /
#              )  |  \  `.___________|/    Whisper API Out of the Box (Where is my ⭐?)
#              `--'   `--'
# ==============================================================================

import torch
import gc
import asyncio
import threading
import traceback
import datetime

from asyncio import Queue
from typing import Optional
from app.utils.logging_utils import configure_logging

# OpenAI Whisper 模型 | OpenAI Whisper model
import whisper

# Faster-Whisper 模型 | Faster-Whisper model
from faster_whisper import WhisperModel


# 异步模型池 | Async model pool
class AsyncModelPool:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super(AsyncModelPool, cls).__new__(cls)
        return cls._instance

    def __init__(self,
                 # 引擎名称 | Engine name
                 engine: str,

                 # openai_whisper 引擎设置 | openai_whisper Engine Settings
                 openai_whisper_model_name: str,
                 openai_whisper_device: str,
                 openai_whisper_download_root: Optional[str],
                 openai_whisper_in_memory: bool,

                 # faster_whisper 引擎设置 | faster_whisper Engine Settings
                 faster_whisper_model_size_or_path: str,
                 faster_whisper_device: str,
                 faster_whisper_device_index: int,
                 faster_whisper_compute_type: str,
                 faster_whisper_cpu_threads: int,
                 faster_whisper_num_workers: int,
                 faster_whisper_download_root: Optional[str],

                 # 模型池设置 | Model Pool Settings
                 min_size: int = 1,
                 max_size: int = 3,
                 create_with_max_concurrent_tasks: bool = True,
                 ):
        """
        初始化异步模型池

        Initialize the asynchronous model pool.

        :param engine: 引擎名称，目前支持 "openai_whisper", "faster_whisper" | Engine name, currently supports "openai_whisper", "faster_whisper"

        :param openai_whisper_model_name: 模型名称，如 "base", "small", "medium", "large" | Model name, e.g., "base", "small", "medium", "large"
        :param openai_whisper_device: 设备名称，如 "cpu" 或 "cuda"，为 None 时自动选择 | Device name, e.g., "cpu" or "cuda"
        :param openai_whisper_download_root: 模型下载根目录 | Model download root directory
        :param openai_whisper_in_memory: 是否在内存中加载模型 | Whether to load the model in memory

        :param faster_whisper_model_size_or_path: 模型名称或路径 | Model name or path
        :param faster_whisper_device: 设备名称，如 "cpu" 或 "cuda"，为 None 时自动选择 | Device name, e.g., "cpu" or "cuda"
        :param faster_whisper_device_index: 设备ID，当 faster_whisper_device 为 "cuda" 时有效 | Device ID, valid when faster_whisper_device is "cuda"
        :param faster_whisper_compute_type: 模型推理计算类型 | Model inference calculation type
        :param faster_whisper_cpu_threads: 模型使用的CPU线程数，设置为 0 时使用所有可用的CPU线程 | The number of CPU threads used by the model, set to 0 to use all available CPU threads
        :param faster_whisper_num_workers: 模型worker数 | Model worker count
        :param faster_whisper_download_root: 模型下载根目录 | Model download root directory

        :param create_with_max_concurrent_tasks: 是否在模型池初始化时以最大并发任务数创建模型实例 |
                                                Whether to create model instances with the maximum number of concurrent tasks
                                                when the model pool is initialized
        :param min_size: 模型池的最小大小 | Minimum pool size
        :param max_size: 模型池的最大大小 | Maximum pool size
        """

        # 防止重复初始化 | Prevent re-initialization
        if getattr(self, '_initialized', False):
            return

        if min_size > max_size:
            raise ValueError("min_size cannot be greater than max_size.")

        self.logger = configure_logging(name=__name__)

        # 模型引擎 | Model engine
        self.engine = engine

        # openai_whisper 引擎设置 | openai_whisper Engine Settings
        self.openai_whisper_model_name = openai_whisper_model_name
        self.openai_whisper_device = self.select_device(openai_whisper_device)
        self.openai_whisper_download_root = openai_whisper_download_root
        self.openai_whisper_in_memory = openai_whisper_in_memory

        # faster_whisper 引擎设置 | faster_whisper Engine Settings
        self.fast_whisper_model_size_or_path = faster_whisper_model_size_or_path
        self.fast_whisper_device = self.select_device(faster_whisper_device)
        self.faster_whisper_device_index = faster_whisper_device_index
        self.fast_whisper_compute_type = faster_whisper_compute_type
        self.fast_whisper_cpu_threads = faster_whisper_cpu_threads
        self.fast_whisper_num_workers = faster_whisper_num_workers
        self.fast_whisper_download_root = faster_whisper_download_root

        self.min_size = min_size
        self.max_size = max_size
        self.create_with_max_concurrent_tasks = create_with_max_concurrent_tasks
        self.pool = Queue(maxsize=max_size)
        self.current_size = 0
        self.size_lock = asyncio.Lock()
        self.resize_lock = asyncio.Lock()
        self.loading_lock = asyncio.Lock()
        self._initialized = True

    @staticmethod
    def select_device(device: Optional[str] = None) -> str:
        """
        选择要使用的设备

        Selects the device to use.

        :param device: 指定的设备名称（可选），"cpu" 或 "cuda"。如果为 None，则自动选择 |
                       Optional device name, "cpu" or "cuda". If None, auto-selects based on availability.
        :return: 已选择的设备名称 | The selected device name
        :raises ValueError: 如果指定的设备无效或不可用 | If the specified device is invalid or unavailable
        """
        if device not in {None, "cpu", "cuda", "auto"}:
            raise ValueError("Invalid device specified. Choose 'cpu', 'cuda', or leave it as None to auto-select.")

        selected_device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if selected_device.startswith("cuda") and not torch.cuda.is_available():
            raise ValueError("CUDA device is not available. Please ensure CUDA is installed and accessible.")

        return selected_device

    async def initialize_pool(self) -> None:
        """
        异步初始化模型池，加载最小数量的模型实例。

        Initialize the model pool asynchronously by loading the minimum number of model instances.
        """

        # 在模型池初始化时的数量 | Number of model instances to create during model pool initialization
        instances_to_create = self.max_size if self.create_with_max_concurrent_tasks else self.min_size

        self.logger.info(f"Initializing AsyncModelPool with {instances_to_create} instances...")

        try:
            async with self.loading_lock:
                if self.current_size >= self.min_size:
                    self.logger.info("AsyncModelPool is already initialized.")
                    return

                tasks = [self._create_and_put_model() for _ in range(instances_to_create)]
                await asyncio.gather(*tasks)
                self.logger.info(f"Successfully initialized AsyncModelPool with {instances_to_create} instances.")

        except Exception as e:
            self.logger.error(f"Failed to initialize AsyncModelPool: {e}")
            self.logger.debug(traceback.format_exc())

    async def _get_model_instance_info(self) -> dict:
        """
        获取模型实例信息。

        Get model instance information.

        :return: 模型实例信息 | Model instance information
        :raises ValueError: 如果指定的引擎不等于 "openai_whisper" 或 "faster_whisper" | If the specified engine is not "openai_whisper" or "faster_whisper"
        """
        if self.engine == "openai_whisper":
            return {
                "model_name": self.openai_whisper_model_name,
                "device": self.openai_whisper_device,
                "download_root": self.openai_whisper_download_root,
                "in_memory": self.openai_whisper_in_memory
            }
        elif self.engine == "faster_whisper":
            return {
                "model_name": self.fast_whisper_model_size_or_path,
                "device": self.fast_whisper_device,
                "device_index": self.faster_whisper_device_index,
                "compute_type": self.fast_whisper_compute_type,
                "cpu_threads": self.fast_whisper_cpu_threads,
                "num_workers": self.fast_whisper_num_workers,
                "download_root": self.fast_whisper_download_root
            }
        else:
            raise ValueError("Invalid engine specified. Choose 'openai_whisper' or 'faster_whisper'.")

    async def _create_and_put_model(self) -> None:
        """
        异步创建新的模型实例并放入池中。

        Asynchronously create a new model instance and put it into the pool.
        """
        try:
            # 开始时间 | Start time
            start_time = datetime.datetime.now()

            # 获取模型实例信息 | Get model instance information
            instance_info = await self._get_model_instance_info()
            self.logger.info(f"""
            Attempting to create a new model instance:
            Engine           : {self.engine}
            Model name       : {instance_info.get("model_name")}
            Device           : {instance_info.get("device")}
            Current pool size: {self.current_size}
            """)

            # 创建模型实例 | Create model instance

            if self.engine == "openai_whisper":
                model = await asyncio.to_thread(
                    whisper.load_model,
                    self.openai_whisper_model_name,
                    device=self.openai_whisper_device,
                    download_root=self.openai_whisper_download_root,
                    in_memory=self.openai_whisper_in_memory
                )
            elif self.engine == "faster_whisper":
                model = await asyncio.to_thread(
                    WhisperModel,
                    self.fast_whisper_model_size_or_path,
                    device=self.fast_whisper_device,
                    device_index=self.faster_whisper_device_index,
                    compute_type=self.fast_whisper_compute_type,
                    cpu_threads=self.fast_whisper_cpu_threads,
                    num_workers=self.fast_whisper_num_workers,
                    download_root=self.fast_whisper_download_root
                )
            else:
                raise ValueError("Invalid engine specified. Choose 'openai_whisper' or 'faster_whisper'.")

            # 结束时间 | End time
            end_time = datetime.datetime.now()

            # 将模型放入池中 | Put model into the pool
            await self.pool.put(model)

            # 更新池大小 | Update pool size
            async with self.size_lock:
                self.current_size += 1

            instance_info = await self._get_model_instance_info()
            self.logger.info(f"""
            Successfully created and added a new model instance to the pool.
            Engine           : {self.engine}
            Model name       : {instance_info.get("model_name")}
            Device           : {instance_info.get("device")}
            Current pool size: {self.current_size}
            Time taken       : {end_time - start_time} seconds
            """)

        except Exception as e:
            self.logger.error(f"Failed to create and add model instance to the pool: {e}")
            self.logger.debug(traceback.format_exc())

    async def get_model(self, timeout: Optional[float] = 5.0):
        """
        异步获取模型实例。如果池为空且未达到最大大小，则创建新的模型实例。

        Asynchronously retrieve a model instance. If the pool is empty and the maximum pool size
        has not been reached, a new model instance will be created.

        :param timeout: 超时时间（以秒为单位），用于等待从池中获取模型实例。默认为 5 秒。
                        Timeout in seconds for waiting to retrieve a model instance from the pool.
                        Defaults to 5 seconds.

        :return: 模型实例 Model instance

        :raises RuntimeError: 当模型池已达到最大大小，且所有实例都正在使用时引发异常。
                              Raised if the model pool is at maximum size and all instances are in use.
        """
        self.logger.info("Attempting to retrieve a model instance from the pool...")
        try:
            # 如果当前池大小小于最大大小，则创建新的模型实例 | Create a new model instance if the current pool size is less than the max size
            if self.current_size < self.max_size:
                async with self.resize_lock:
                    async with self.size_lock:
                        add_count = self.max_size - self.current_size
                        tasks = [self._create_and_put_model() for _ in range(add_count)]
                        await asyncio.gather(*tasks)
                        self.current_size += add_count
                        self.logger.info(f"""
                        Pool was below maximum size. Created {add_count} new model instances.
                        New current pool size: {self.current_size} / Max size: {self.max_size}
                        """)

            # 从池中获取模型实例 | Retrieve model instance from the pool
            model = await asyncio.wait_for(self.pool.get(), timeout=timeout)
            self.logger.info(f"""
            Model instance successfully retrieved from the pool.
            Current pool size: {self.current_size} / Max size: {self.max_size}
            """)
            return model
        except asyncio.TimeoutError:
            self.logger.warning(
                f"Timeout ({timeout} seconds) while waiting to retrieve a model instance from the pool.")

            async with self.resize_lock:
                async with self.size_lock:
                    if self.current_size < self.max_size:
                        await self._create_and_put_model()
                        self.current_size += 1
                        self.logger.warning(f"""
                        Pool was empty. Created a new model instance due to pool exhaustion.
                        New current pool size: {self.current_size} / Max size: {self.max_size}
                        """)
                        # 从池中获取刚创建的模型实例 | Retrieve the newly created model instance from the pool
                        model = await self.pool.get()
                        return model
                    else:
                        self.logger.error(f"""
                        Model pool exhausted and all models are currently in use.
                        Current pool size: {self.current_size} / Max size: {self.max_size}
                        """)
                        raise RuntimeError("Model pool exhausted, and all models are currently in use.")

    async def return_model(self, model) -> None:
        """
        将模型实例归还到池中。

        Return a model instance to the pool.

        :param model: 要归还的模型实例 | The model instance to return
        """
        try:
            # 检查池是否已满 | Check if the pool is already full
            if self.pool.full():
                self.logger.warning(f"""
                Model pool is full. Unable to return model instance.
                Model will be destroyed to prevent resource leak.
                """)
                await self._destroy_model(model)
                return

            # 尝试将模型放入池中 | Try to return the model to the pool
            await self.pool.put(model)
            self.logger.info(f"""
            Model instance successfully returned to the pool.
            Current pool size (after return): {self.pool.qsize()}
            """)
        except (RuntimeError, AttributeError) as e:
            # 捕获模型实例无效的情况 | Catch cases where the model instance is invalid
            self.logger.error(f"Failed to return model to pool due to invalid model instance: {str(e)}", exc_info=True)
            await self._destroy_model(model)
        except Exception as e:
            # 捕获任何其他未预料到的异常 | Capture any other unexpected exceptions
            self.logger.error(f"An unexpected error occurred while returning model to pool: {str(e)}", exc_info=True)
            await self._destroy_model(model)

    async def _is_model_healthy(self, model):
        """
        异步检查模型实例是否健康。

        Asynchronously check if the model instance is healthy.

        :param model: 要检查的模型实例 The model instance to check
        :return: True 如果模型健康，否则 False True if the model is healthy, False otherwise
        """
        try:
            instance_info = await self._get_model_instance_info()
            dummy_input = torch.zeros(1, 80, 300).to(instance_info.get("device"))
            with torch.no_grad():
                await asyncio.to_thread(model.encode, dummy_input)
            return True
        except Exception:
            self.logger.error("Model health check failed.")
            return False

    async def _destroy_model(self, model) -> None:
        """
        销毁模型实例并更新池大小。

        Destroy a model instance and update the pool size.

        :param model: 要销毁的模型实例 | The model instance to destroy
        """
        try:
            # 删除模型实例的引用 | Explicitly delete the model instance reference
            del model

            # 如果使用 GPU 则清理 CUDA 缓存 | Clear CUDA cache if using GPU
            instance_info = await self._get_model_instance_info()
            if instance_info.get("device").startswith("cuda"):
                torch.cuda.empty_cache()
                self.logger.info("CUDA cache cleared after model destruction.")

            # 执行垃圾回收 | Perform garbage collection on any device
            gc.collect()
            self.logger.info("Garbage collection performed after model destruction.")

            # 更新池大小，确保减少当前池大小 | Update pool size to reflect the reduced pool size
            async with self.size_lock:
                self.current_size = max(0, self.current_size - 1)
                self.logger.info(f"""
                Model instance destroyed successfully.
                Updated pool size: {self.current_size}
                Minimum pool size: {self.min_size}
                """)

        except Exception as e:
            self.logger.error(f"Failed to destroy model instance: {str(e)}", exc_info=True)

    async def resize_pool(self, new_min_size: int, new_max_size: int) -> None:
        """
        异步调整模型池的大小。

        Asynchronously resize the model pool.

        :param new_min_size: 新的最小池大小 | New minimum pool size
        :param new_max_size: 新的最大池大小 | New maximum pool size
        """
        if new_min_size > new_max_size:
            raise ValueError("new_min_size cannot be greater than new_max_size.")

        self.logger.info(f"Resizing model pool with new minimum size: {new_min_size}, new maximum size: {new_max_size}")

        async with self.resize_lock:
            self.min_size = new_min_size
            self.max_size = new_max_size

            async with self.size_lock:
                if self.current_size < self.min_size:
                    # 增加模型实例 | Increase model instances to meet new min size
                    add_count = self.min_size - self.current_size
                    tasks = [self._create_and_put_model() for _ in range(add_count)]
                    await asyncio.gather(*tasks)
                    self.logger.info(f"""
                    Resized pool: Created {add_count} new model instances.
                    Current pool size: {self.current_size}
                    Minimum pool size: {self.min_size}
                    Maximum pool size: {self.max_size}
                    """)
                elif self.current_size > self.max_size:
                    # 减少模型实例 | Remove model instances to meet new max size
                    remove_count = self.current_size - self.max_size
                    tasks = []
                    for _ in range(remove_count):
                        if not self.pool.empty():
                            model = await self.pool.get()
                            tasks.append(self._destroy_model(model))
                    await asyncio.gather(*tasks)
                    self.logger.info(f"""
                    Resized pool: Removed {remove_count} excess model instances.
                    Current pool size: {self.current_size}
                    Minimum pool size: {self.min_size}
                    Maximum pool size: {self.max_size}
                    """)
