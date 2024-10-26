import asyncio
import os
import tempfile
import aiofiles
import uuid
import re
import stat
import filetype

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
            temp_dir: str = './temp_files'
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
        # 配置日志记录器 | Configure the logger
        self.logger = configure_logging(name=__name__)

        # 设置 umask，确保新创建的文件权限为 600 | Set umask to ensure new files have 600 permissions
        if os.name != 'nt':  # 在非 Windows 系统上设置 umask
            os.umask(0o077)

        # 将 temp_dir 转换为基于当前工作目录的绝对路径 | Convert temp_dir to an absolute path
        if temp_dir:
            # 创建临时目录 | Create temporary directory
            os.makedirs(temp_dir, exist_ok=True)
            self.TEMP_DIR = os.path.abspath(temp_dir)
            self.temp_dir_obj = None

            # 在非 Windows 系统上设置目录权限
            if os.name != 'nt':
                os.chmod(self.TEMP_DIR, stat.S_IRWXU)  # 设置目录权限为 700 | Set directory permissions to 700
            self.logger.debug(f"Temporary directory set to {self.TEMP_DIR}")
        else:
            # 如果未提供 temp_dir，则使用系统临时目录 | Use system temporary directory if temp_dir is not provided
            self.temp_dir_obj = tempfile.TemporaryDirectory()
            self.TEMP_DIR = self.temp_dir_obj.name
            if os.name != 'nt':
                os.chmod(self.TEMP_DIR, stat.S_IRWXU)
            self.logger.debug(f"Using system temporary directory {self.TEMP_DIR}")

        # 配置类属性 | Configure class attributes
        self.AUTO_DELETE = auto_delete
        self.LIMIT_FILE_SIZE = limit_file_size
        self.MAX_FILE_SIZE = max_file_size
        self.CHUNK_SIZE = chunk_size
        self.BATCH_SIZE = batch_size
        self.DELETE_BATCH_SIZE = delete_batch_size

        # 定义允许的文件扩展名（FFmpeg 支持的媒体文件）| Define allowed file extensions (FFmpeg supported media files)
        self.ALLOWED_EXTENSIONS = [
            '.3g2', '.3gp', '.aac', '.ac3', '.aiff', '.alac', '.amr', '.ape', '.asf', '.avi', '.avs', '.cavs', '.dirac',
            '.dts', '.dv', '.eac3', '.f4v', '.flac', '.flv', '.g722', '.g723_1', '.g726', '.g729', '.gif', '.gsm',
            '.h261', '.h263', '.h264', '.hevc', '.jpeg', '.jpg', '.lpcm', '.m4a', '.m4v', '.mkv', '.mlp', '.mmf',
            '.mov', '.mp2', '.mp3', '.mp4', '.mpc', '.mpeg', '.mpg', '.oga', '.ogg', '.ogv', '.opus', '.png', '.rm',
            '.rmvb', '.rtsp', '.sbc', '.spx', '.svcd', '.swf', '.tak', '.thd', '.tta', '.vc1', '.vcd', '.vid', '.vob',
            '.wav', '.wma', '.wmv', '.wv', '.webm', '.yuv'
        ]

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
        file_path = os.path.realpath(file_path)
        # 确保文件路径在 TEMP_DIR 内部 | Ensure file path is within TEMP_DIR
        if not file_path.startswith(os.path.realpath(self.TEMP_DIR) + os.sep):
            self.logger.error("Invalid file path detected.")
            raise ValueError("Invalid file path detected.")

        # 检查是否为符号链接 | Check if the path is a symbolic link
        if os.path.islink(file_path):
            self.logger.error("Symbolic links are not allowed.")
            raise ValueError("Invalid file path detected.")

        try:
            # 检查文件大小限制 | Check file size limit
            if self.LIMIT_FILE_SIZE and len(file) > self.MAX_FILE_SIZE:
                error_msg = f"File size exceeds the limit: {len(file)} > {self.MAX_FILE_SIZE}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            # 异步写入文件 | Asynchronously write file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file)
            # 设置文件权限，仅所有者可读写 | Set file permissions to 600
            if os.name != 'nt':  # 在非 Windows 系统上设置权限
                await asyncio.to_thread(os.chmod, file_path, stat.S_IRUSR | stat.S_IWUSR)

            # 文件类型验证 | File type validation
            if not self.is_allowed_file_type(file_path):
                self.logger.error("File type is not supported.")
                await self.delete_file(file_path)
                raise ValueError("File type is not supported.")

            self.logger.debug("File saved successfully.")
            return file_path
        except (OSError, IOError) as e:
            self.logger.error("Failed to save file due to an exception.")
            raise ValueError("An error occurred while saving the file.")

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
        file_path = os.path.realpath(file_path)
        # 确保文件路径在 TEMP_DIR 内部 | Ensure file path is within TEMP_DIR
        if not file_path.startswith(os.path.realpath(self.TEMP_DIR) + os.sep):
            self.logger.error("Invalid file path detected.")
            raise ValueError("Invalid file path detected.")

        # 检查是否为符号链接 | Check if the path is a symbolic link
        if os.path.islink(file_path):
            self.logger.error("Symbolic links are not allowed.")
            raise ValueError("Invalid file path detected.")

        try:
            file_size = 0
            # 异步读取和写入文件，支持大文件 | Asynchronously read and write file, supports large files
            async with aiofiles.open(file_path, 'wb') as f:
                while True:
                    content = await file.read(self.CHUNK_SIZE)
                    if not content:
                        break
                    file_size += len(content)
                    # 检查文件大小限制 | Check file size limit
                    if self.LIMIT_FILE_SIZE and file_size > self.MAX_FILE_SIZE:
                        error_msg = f"File size exceeds the limit: {file_size} > {self.MAX_FILE_SIZE}"
                        self.logger.error(error_msg)
                        raise ValueError(error_msg)
                    await f.write(content)
            # 设置文件权限，仅所有者可读写 | Set file permissions to 600
            if os.name != 'nt':
                await asyncio.to_thread(os.chmod, file_path, stat.S_IRUSR | stat.S_IWUSR)

            # 文件类型验证 | File type validation
            if not self.is_allowed_file_type(file_path):
                self.logger.error(f"File type is not supported.")
                await self.delete_file(file_path)
                raise ValueError("File type is not supported.")

            self.logger.debug("Uploaded file saved successfully.")
            return file_path
        except (OSError, IOError, ValueError) as e:
            self.logger.error("Failed to save uploaded file due to an exception.")
            raise ValueError("An error occurred while saving the uploaded file.")

    async def delete_files_in_batch(self, file_paths: List[str]) -> None:
        """
        异步批量删除文件 | Asynchronously delete files in batches.

        参数 | Parameters:
            file_paths (List[str]): 要删除的文件路径列表 | List of file paths to delete.

        返回 | Returns:
            None
        """
        semaphore = asyncio.Semaphore(self.DELETE_BATCH_SIZE)

        async def sem_delete(file_path):
            async with semaphore:
                await self.delete_file(file_path)

        try:
            tasks = [sem_delete(file_path) for file_path in file_paths]
            await asyncio.gather(*tasks)
            self.logger.debug("Batch of files deleted successfully.")
        except Exception as e:
            self.logger.error("Failed to delete batch of files due to an exception.")
            raise ValueError("An error occurred while deleting files.")

    async def delete_file(self, file_path: str) -> None:
        """
        异步删除单个文件 | Asynchronously delete a single file.

        参数 | Parameters:
            file_path (str): 要删除的文件路径 | Path of the file to delete.

        返回 | Returns:
            None
        """
        file_path = os.path.realpath(file_path)
        # 确保文件路径在 TEMP_DIR 内部 | Ensure file path is within TEMP_DIR
        if not file_path.startswith(os.path.realpath(self.TEMP_DIR) + os.sep):
            self.logger.warning("Attempted to delete file outside of TEMP_DIR.")
            return

        # 检查是否为符号链接 | Check if the path is a symbolic link
        if os.path.islink(file_path):
            self.logger.warning("Symbolic links are not allowed.")
            return

        try:
            # 检查文件是否为常规文件 | Check if the file is a regular file
            file_stat = await asyncio.to_thread(os.lstat, file_path)
            if not stat.S_ISREG(file_stat.st_mode):
                self.logger.warning("Not a regular file.")
                return
            # 异步删除文件 | Asynchronously delete the file
            await asyncio.to_thread(os.remove, file_path)
            self.logger.debug("Deleted file successfully.")
        except FileNotFoundError:
            self.logger.warning("File not found.")
        except (OSError, IOError) as e:
            self.logger.error("Failed to delete file due to an exception.")
            raise ValueError("An error occurred while deleting the file.")

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
                # 获取临时目录中的所有文件路径 | Get all file paths in TEMP_DIR
                file_paths = [
                    os.path.join(self.TEMP_DIR, f)
                    for f in os.listdir(self.TEMP_DIR)
                    if os.path.isfile(os.path.join(self.TEMP_DIR, f))
                ]
                # 分批删除文件 | Delete files in batches
                for i in range(0, len(file_paths), self.DELETE_BATCH_SIZE):
                    batch = file_paths[i:i + self.DELETE_BATCH_SIZE]
                    await self.delete_files_in_batch(batch)
                self.logger.debug("All temporary files have been cleaned up.")
            except (OSError, IOError) as e:
                self.logger.error("Failed to clean up temporary files due to an exception.")
                raise ValueError("An error occurred while cleaning up temporary files.")

    def _generate_safe_file_name(self, original_name: str) -> str:
        """
        生成安全且唯一的文件名 | Generate a safe and unique file name.

        参数 | Parameters:
            original_name (str): 原始文件名 | Original file name.

        返回 | Returns:
            str: 安全且唯一的文件名 | Safe and unique file name.
        """
        # 获取文件的扩展名，并限制为合法字符 | Get file extension and allow only safe characters
        _, ext = os.path.splitext(original_name)
        ext = re.sub(r'[^\w\.]', '', ext)
        ext = ext.lower()
        if len(ext) > 10:
            ext = ext[:10]
        # 生成唯一的文件名 | Generate a unique file name
        unique_name = f"{uuid.uuid4().hex}{ext}"
        self.logger.debug("Generated unique file name.")
        return unique_name

    def is_allowed_file_type(self, file_path: str) -> bool:
        """
        检查文件是否为允许的类型 | Check if the file is of an allowed type.

        参数 | Parameters:
            file_path (str): 文件路径 | Path to the file.

        返回 | Returns:
            bool: 如果文件类型被允许则返回 True，否则返回 False | True if the file type is allowed, False otherwise.
        """
        try:
            # 使用 filetype 库检测文件类型 | Detect file type using filetype library
            kind = filetype.guess(file_path)
            if kind is None:
                self.logger.error("Unable to determine file type.")
                return False
            ext = f'.{kind.extension}'.lower()
            if ext in self.ALLOWED_EXTENSIONS:
                return True
            else:
                self.logger.error(f"File type {ext} is not supported.")
                return False
        except Exception as e:
            self.logger.error(f"Unable to determine file type: {str(e)}")
            return False

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
        # 等待清理任务完成，确保资源释放 | Wait for cleanup tasks to complete
        await self.cleanup_temp_files()
        # 仅在使用系统临时目录时清理目录 | Clean up the directory if using system temp directory
        if self.temp_dir_obj:
            await asyncio.to_thread(self.temp_dir_obj.cleanup)
            self.logger.debug(
                f"System temporary directory {self.TEMP_DIR} has been cleaned up.")
