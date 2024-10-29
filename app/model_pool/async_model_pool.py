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

import asyncio
import threading
import traceback
from asyncio import Queue
from typing import Optional
from app.utils.logging_utils import configure_logging
import whisper
import torch
import gc


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

    def __init__(self, model_name: str, device: str = None,
                 download_root: Optional[str] = None, in_memory: bool = False,
                 min_size: int = 1, max_size: int = 3,
                 create_with_max_concurrent_tasks: bool = True
                 ):
        """
        初始化异步模型池

        Initialize the asynchronous model pool.

        :param model_name: 模型名称，如 "base", "small", "medium", "large" | Model name, e.g., "base", "small", "medium", "large"
        :param device: 设备名称，如 "cpu" 或 "cuda"，为 None 时自动选择 | Device name, e.g., "cpu" or "cuda"
        :param download_root: 模型下载根目录 | Model download root directory
        :param in_memory: 是否在内存中加载模型 | Whether to load the model in memory
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
        self.model_name = model_name
        self.device = self.select_device(device)
        self.download_root = download_root
        self.in_memory = in_memory
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
        if device not in {None, "cpu", "cuda"}:
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

    async def _create_and_put_model(self) -> None:
        """
        异步创建新的模型实例并放入池中。

        Asynchronously create a new model instance and put it into the pool.
        """
        try:
            self.logger.info(f"""
            Attempting to create a new model instance:
            Model name       : {self.model_name}
            Device           : {self.device}
            Current pool size: {self.current_size}
            """)

            # 创建模型实例 | Create model instance
            model = await asyncio.to_thread(
                whisper.load_model,
                self.model_name,
                device=self.device,
                download_root=self.download_root,
                in_memory=self.in_memory
            )

            # 将模型放入池中 | Put model into the pool
            await self.pool.put(model)

            # 更新池大小 | Update pool size
            async with self.size_lock:
                self.current_size += 1

            self.logger.info(f"""
            Successfully created and added a new model instance to the pool.
            Model name       : {self.model_name}
            Device           : {self.device}
            Current pool size: {self.current_size}
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
            dummy_input = torch.zeros(1, 80, 300).to(self.device)
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
            if self.device == "cuda":
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
