import asyncio
import os
import tempfile
import aiofiles
import uuid
from typing import List, Any, Optional
from fastapi import UploadFile
from app.utils.logging_utils import configure_logging


class FileUtils:
    """
    文件处理工具类 | File utility class for asynchronous file operations.
    """

    def __init__(
            self,
            chunk_size: int = 1024 * 1024,
            batch_size: int = 10,
            delete_batch_size: int = 5,
            auto_delete: bool = True,
            limit_file_size: bool = True,
            max_file_size: int = 2 * 1024 * 1024 * 1024,
            temp_dir: str = './Temp_Files'
    ) -> None:
        """
        初始化 FileUtils 实例 | Initialize the FileUtils instance.

        参数 | Parameters:
            chunk_size (int): 文件读取块大小，默认1MB | File read chunk size, default is 1MB.
            batch_size (int): 分批处理的批大小，默认10 | Batch size for processing files, default is 10.
            delete_batch_size (int): 文件删除批大小，默认5 | Batch size for deleting files, default is 5.
            auto_delete (bool): 是否自动删除临时文件，默认True | Whether to auto-delete temporary files, default is True.
            limit_file_size (bool): 是否限制文件大小，默认True | Whether to limit file size, default is True.
            max_file_size (int): 最大文件大小（字节），默认2GB | Maximum file size in bytes, default is 2GB.
            temp_dir (str): 临时文件夹路径，默认'./Temp_Files' | Temporary directory path, default is './Temp_Files'.

        返回 | Returns:
            None
        """
        # 配置日志记录器
        self.logger = configure_logging(name=__name__)
        
        # 将 temp_dir 转换为基于当前工作目录的绝对路径
        if temp_dir:
            self.TEMP_DIR = os.path.abspath(temp_dir)
            self.temp_dir_obj = None
            # 确保目录存在
            os.makedirs(self.TEMP_DIR, exist_ok=True)
            self.logger.debug(f"Temporary directory set to {self.TEMP_DIR}")
        else:
            # 如果未提供 temp_dir，则使用系统临时目录
            self.temp_dir_obj = tempfile.TemporaryDirectory()
            self.TEMP_DIR = self.temp_dir_obj.name
            self.logger.debug(f"Using system temporary directory {self.TEMP_DIR}")

        # 配置类属性
        self.AUTO_DELETE = auto_delete
        self.LIMIT_FILE_SIZE = limit_file_size
        self.MAX_FILE_SIZE = max_file_size
        self.CHUNK_SIZE = chunk_size
        self.BATCH_SIZE = batch_size
        self.DELETE_BATCH_SIZE = delete_batch_size

    async def save_file(self, file: bytes, file_name: str) -> str:
        """
        保存字节文件到临时目录 | Save a bytes file to the temporary directory.

        参数 | Parameters:
            file (bytes): 要保存的文件内容 | Content of the file to save.
            file_name (str): 原始文件名 | Original file name.

        返回 | Returns:
            str: 保存的文件路径 | Path to the saved file.
        """
        safe_file_name = self._generate_safe_file_name(file_name)
        file_path = os.path.join(self.TEMP_DIR, safe_file_name)
        try:
            # 检查文件大小限制
            if self.LIMIT_FILE_SIZE and len(file) > self.MAX_FILE_SIZE:
                error_msg = "文件大小超过限制 | File size exceeds the limit."
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            # 异步写入文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file)
            self.logger.debug(f"File saved successfully at {file_path}.")
            return file_path
        except (OSError, IOError) as e:
            self.logger.error(f"Failed to save file at {file_path}: {str(e)}")
            raise

    async def save_uploaded_file(self, file: UploadFile) -> str:
        """
        保存FastAPI上传的文件到临时目录 | Save an uploaded file from FastAPI to the temporary directory.

        参数 | Parameters:
            file (UploadFile): FastAPI上传的文件对象 | File object uploaded via FastAPI.

        返回 | Returns:
            str: 保存的文件路径 | Path to the saved file.
        """
        safe_file_name = self._generate_safe_file_name(file.filename)
        file_path = os.path.join(self.TEMP_DIR, safe_file_name)
        try:
            file_size = 0
            # 异步读取和写入文件，支持大文件
            async with aiofiles.open(file_path, 'wb') as f:
                while True:
                    content = await file.read(self.CHUNK_SIZE)
                    if not content:
                        break
                    file_size += len(content)
                    # 检查文件大小限制
                    if self.LIMIT_FILE_SIZE and file_size > self.MAX_FILE_SIZE:
                        error_msg = "文件大小超过限制 | File size exceeds the limit."
                        self.logger.error(error_msg)
                        raise ValueError(error_msg)
                    await f.write(content)
            self.logger.debug(f"Uploaded file saved successfully at {file_path}.")
            return file_path
        except (OSError, IOError, ValueError) as e:
            self.logger.error(f"Failed to save uploaded file at {file_path}: {str(e)}")
            raise

    async def delete_files_in_batch(self, file_paths: List[str]) -> None:
        """
        异步批量删除文件 | Asynchronously delete files in batches.

        参数 | Parameters:
            file_paths (List[str]): 要删除的文件路径列表 | List of file paths to delete.

        返回 | Returns:
            None
        """
        try:
            # 创建删除文件的任务列表
            tasks = [self.delete_file(file_path) for file_path in file_paths]
            # 并发执行删除操作
            await asyncio.gather(*tasks)
            self.logger.debug("Batch of files deleted successfully.")
        except Exception as e:
            self.logger.error(f"Failed to delete batch of files: {str(e)}")
            raise

    async def delete_file(self, file_path: str) -> None:
        """
        异步删除单个文件 | Asynchronously delete a single file.

        参数 | Parameters:
            file_path (str): 要删除的文件路径 | Path of the file to delete.

        返回 | Returns:
            None
        """
        try:
            # 检查文件是否存在
            if os.path.exists(file_path):
                # 异步删除文件
                await asyncio.to_thread(os.remove, file_path)
                self.logger.debug(f"Deleted file {file_path}.")
            else:
                self.logger.warning(f"File not found: {file_path}")
        except (OSError, IOError) as e:
            self.logger.error(f"Failed to delete file {file_path}: {str(e)}")
            raise

    async def cleanup_temp_files(self) -> None:
        """
        清理所有临时文件 | Clean up all temporary files.

        参数 | Parameters:
            None

        返回 | Returns:
            None
        """
        if self.AUTO_DELETE:
            try:
                # 获取临时目录中的所有文件路径
                file_paths = [
                    os.path.join(self.TEMP_DIR, f)
                    for f in os.listdir(self.TEMP_DIR)
                    if os.path.isfile(os.path.join(self.TEMP_DIR, f))
                ]
                # 分批删除文件
                for i in range(0, len(file_paths), self.DELETE_BATCH_SIZE):
                    batch = file_paths[i:i + self.DELETE_BATCH_SIZE]
                    await self.delete_files_in_batch(batch)
                self.logger.debug("All temporary files have been cleaned up.")
            except (OSError, IOError) as e:
                self.logger.error(f"Failed to clean up temporary files: {str(e)}")
                raise

    def _generate_safe_file_name(self, original_name: str) -> str:
        """
        生成安全且唯一的文件名 | Generate a safe and unique file name.

        参数 | Parameters:
            original_name (str): 原始文件名 | Original file name.

        返回 | Returns:
            str: 安全且唯一的文件名 | Safe and unique file name.
        """
        # 获取文件的基础名称
        base_name = os.path.basename(original_name)
        # 生成唯一的文件名
        unique_name = f"{uuid.uuid4().hex}_{base_name}"
        self.logger.debug(f"Generated unique file name: {unique_name}")
        return unique_name

    async def __aenter__(self) -> 'FileUtils':
        """
        进入异步上下文管理器 | Enter the asynchronous context manager.

        参数 | Parameters:
            None

        返回 | Returns:
            FileUtils: 文件工具类的实例 | Instance of the FileUtils class.
        """
        self.logger.debug("Entering FileUtils context manager.")
        return self

    async def __aexit__(
            self,
            exc_type: Optional[type],
            exc_val: Optional[BaseException],
            exc_tb: Optional[Any]
    ) -> None:
        """
        退出异步上下文管理器，清理资源 | Exit the asynchronous context manager and clean up resources.

        参数 | Parameters:
            exc_type (Optional[type]): 异常类型 | Exception type.
            exc_val (Optional[BaseException]): 异常值 | Exception value.
            exc_tb (Optional[Any]): Traceback对象 | Traceback object.

        返回 | Returns:
            None
        """
        self.logger.debug("Exiting FileUtils context manager.")
        await self.cleanup_temp_files()
        # 仅在使用系统临时目录时清理目录
        if self.temp_dir_obj:
            self.temp_dir_obj.cleanup()
            self.logger.debug(f"System temporary directory {self.TEMP_DIR} has been cleaned up.")

# 使用示例 | Usage example
# async def main():
#     async with FileUtils() as file_utils:
#         file_path = await file_utils.save_file(b'content', 'example.txt')
#         # 执行其他操作 | Perform other operations
#         print(f"File saved at: {file_path}")

# if __name__ == "__main__":
#     asyncio.run(main())
