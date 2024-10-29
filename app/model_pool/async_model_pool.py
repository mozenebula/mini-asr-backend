import asyncio
import threading
import traceback
from asyncio import Queue
from typing import Optional
from config.settings import Settings
from app.utils.logging_utils import configure_logging
import whisper
import torch
import gc


# 异步模型池 Async model pool
class AsyncModelPool:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super(AsyncModelPool, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_name: str, device: str = None, min_size: int = 1,
                 max_size: int = Settings.WhisperSettings.MAX_CONCURRENT_TASKS):
        """
        初始化异步模型池 Initialize the asynchronous model pool.

        :param model_name: 模型名称，如 "base", "small", "medium", "large"
                          Model name, e.g., "base", "small", "medium", "large"
        :param device: 设备名称，如 "cpu" 或 "cuda"
                      Device name, e.g., "cpu" or "cuda"
        :param min_size: 池的最小大小 Minimum pool size
        :param max_size: 池的最大大小 Maximum pool size
        """
        if getattr(self, '_initialized', False):
            return  # 防止重复初始化 Prevent re-initialization

        self.logger = configure_logging(name=__name__)
        self.logger.info("Initializing AsyncModelPool...")

        device = self.select_device(device)

        if min_size > max_size:
            raise ValueError("min_size cannot be greater than max_size.")

        self.model_name = model_name
        self.device = device
        self.min_size = min_size
        self.max_size = max_size
        self.pool = Queue(maxsize=max_size)
        self.current_size = 0
        self.loading_lock = asyncio.Lock()
        self.resize_lock = asyncio.Lock()
        self.size_lock = asyncio.Lock()  # 用于保护 current_size的锁 Lock to protect current_size
        self._initialized = True
        self.logger.info("AsyncModelPool initialized.")

    @staticmethod
    def select_device(device=None):
        if device not in {None, "cpu", "cuda"}:
            raise ValueError("Invalid device specified. Choose 'cpu', 'cuda', or leave it as None to auto-select.")

        selected_device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if selected_device.startswith("cuda") and not torch.cuda.is_available():
            raise ValueError("CUDA device is not available.")

        return selected_device

    async def initialize_pool(self):
        """
        异步初始化模型池，加载最小数量的模型实例。
        Initialize the model pool asynchronously by loading the minimum number of model instances.
        """
        async with self.loading_lock:
            if self.current_size >= self.min_size:
                self.logger.info("AsyncModelPool is already initialized.")
                return
            tasks = [self._create_and_put_model() for _ in range(self.min_size)]
            await asyncio.gather(*tasks)
            self.logger.info(f"Initialized model pool with {self.min_size} models.")

    async def _create_and_put_model(self):
        """
        异步创建新的模型实例并放入池中。
        Asynchronously create a new model instance and put it into the pool.
        """
        model = await self._create_model_instance()
        await self.pool.put(model)
        async with self.size_lock:
            self.current_size += 1
        self.logger.info("Model instance created and added to the pool.")

    async def _create_model_instance(self, download_root: Optional[str] = None, in_memory: bool = False):
        """
        异步创建新的模型实例。
        Asynchronously create a new model instance.

        :param download_root: 模型下载的根目录 | Model download root
        :param in_memory: 是否将模型加载到内存中 | Whether to load the model into memory
        :return: 模型实例 Model instance
        """
        model = await asyncio.to_thread(
            whisper.load_model,
            self.model_name,
            device=self.device,
            download_root=download_root,
            in_memory=in_memory
        )
        self.logger.info("New model instance created.")
        return model

    async def get_model(self, timeout: Optional[float] = None):
        """
        异步获取模型实例。如果池为空且未达到最大大小，则创建新的模型实例。
        Asynchronously retrieve a model instance. If the pool is empty and max size is not reached,
        create a new model instance.

        :param timeout: 获取模型实例的等待超时时间 Timeout for waiting to retrieve a model instance
        :return: 模型实例 Model instance
        """
        try:
            model = await asyncio.wait_for(self.pool.get(), timeout=timeout)
            self.logger.info("Model instance retrieved from pool.")
            return model
        except asyncio.TimeoutError:
            async with self.resize_lock:
                async with self.size_lock:
                    if self.current_size < self.max_size:
                        model = await self._create_model_instance()
                        self.current_size += 1
                        self.logger.warning(
                            "Model pool was empty. Created a new model instance due to pool exhaustion.")
                        return model
                    else:
                        self.logger.error("Model pool exhausted and all models are in use.")
                        raise RuntimeError("Model pool exhausted, and all models are currently in use.")

    async def return_model(self, model):
        """
        将模型实例归还到池中。
        Return a model instance to the pool.

        :param model: 要归还的模型实例 The model instance to return
        """
        if await self._is_model_healthy(model):
            await self.pool.put(model)
            self.logger.info("Model instance returned to the pool.")
        else:
            await self._destroy_model(model)
            self.logger.warning("Unhealthy model instance detected and destroyed.")

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

    async def _destroy_model(self, model):
        """
        销毁模型实例并更新池大小。
        Destroy a model instance and update the pool size.

        :param model: 要销毁的模型实例 The model instance to destroy
        """
        try:
            # 删除模型实例的引用 Explicitly delete the model instance reference
            del model

            if self.device == "cuda":
                torch.cuda.empty_cache()  # 清理 CUDA 缓存 Clear CUDA cache
                self.logger.info("CUDA cache cleared after model destruction.")

            # 在任何设备情况下进行垃圾回收 Perform garbage collection on any device
            gc.collect()
            self.logger.info("Garbage collection performed after model destruction.")

            # 更新池大小 Update pool size
            async with self.size_lock:
                if self.current_size > self.min_size:
                    self.current_size -= 1
                    self.logger.info(f"Model instance destroyed, updated pool size: {self.current_size}")

        except Exception as e:
            error_trace = traceback.format_exc()
            self.logger.error(f"Failed to destroy model instance: {e}\n{error_trace}")

    async def resize_pool(self, new_min_size: int, new_max_size: int):
        """
        异步调整模型池的大小。
        Asynchronously resize the model pool.

        :param new_min_size: 新的最小池大小 New minimum pool size
        :param new_max_size: 新的最大池大小 New maximum pool size
        """
        if new_min_size > new_max_size:
            raise ValueError("new_min_size cannot be greater than new_max_size.")

        async with self.resize_lock:
            self.min_size = new_min_size
            self.max_size = new_max_size

            async with self.size_lock:
                if self.current_size < self.min_size:
                    tasks = [self._create_and_put_model() for _ in range(self.min_size - self.current_size)]
                    await asyncio.gather(*tasks)
                    self.logger.info(f"Resized pool: {self.min_size} minimum models created.")
                elif self.current_size > self.max_size:
                    remove_count = self.current_size - self.max_size
                    for _ in range(remove_count):
                        if not self.pool.empty():
                            model = await self.pool.get()
                            await self._destroy_model(model)
                    self.logger.info(f"Resized pool: Removed {remove_count} excess models.")
