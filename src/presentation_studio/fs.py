from __future__ import annotations

from dataclasses import dataclass
import ctypes
import errno
import os
from pathlib import Path
import stat
from typing import Self


@dataclass
class BoundDirectory:
    path: Path
    descriptor: int
    device: int
    inode: int
    guards: list[int]

    @classmethod
    def open(cls, path: Path, *, allow_delete: bool = False) -> Self:
        path = path.absolute()
        if os.name == "nt":
            import msvcrt

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            create_file = kernel32.CreateFileW
            create_file.argtypes = [
                ctypes.c_wchar_p,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_void_p,
            ]
            create_file.restype = ctypes.c_void_p
            close_handle = kernel32.CloseHandle
            close_handle.argtypes = [ctypes.c_void_p]
            close_handle.restype = ctypes.c_int
            invalid = ctypes.c_void_p(-1).value
            descriptors: list[int] = []
            chain = list(reversed((path, *path.parents)))
            try:
                for item in chain:
                    info = item.lstat()
                    marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
                    if marker and getattr(info, "st_file_attributes", 0) & marker:
                        raise OSError("refusing to bind a reparse-point directory")
                    is_leaf = item == path
                    share = 0x1 | 0x2 | (0x4 if allow_delete and is_leaf else 0)
                    handle = create_file(
                        str(item), 0, share, None, 3, 0x02000000 | 0x00200000, None
                    )
                    if handle in (None, invalid):
                        raise OSError(
                            ctypes.get_last_error(), "cannot bind directory", item
                        )
                    try:
                        descriptor = msvcrt.open_osfhandle(int(handle), os.O_RDONLY)
                    except BaseException:
                        close_handle(handle)
                        raise
                    descriptors.append(descriptor)
            except BaseException:
                for guard in reversed(descriptors):
                    os.close(guard)
                raise
            descriptor = descriptors[-1]
            guards = descriptors[:-1]
        else:
            descriptor = os.open(
                path,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_CLOEXEC", 0),
            )
            guards = []
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISDIR(info.st_mode):
                raise NotADirectoryError(path)
            current = path.stat()
            if (info.st_dev, info.st_ino) != (current.st_dev, current.st_ino):
                raise OSError("directory identity changed while binding")
            return cls(path, descriptor, info.st_dev, info.st_ino, guards)
        except BaseException:
            os.close(descriptor)
            for guard in reversed(guards):
                os.close(guard)
            raise

    def close(self) -> None:
        descriptors: list[int] = []
        if self.descriptor >= 0:
            descriptors.append(self.descriptor)
            self.descriptor = -1
        descriptors.extend(reversed(self.guards))
        self.guards.clear()
        first_error: OSError | None = None
        for descriptor in descriptors:
            try:
                os.close(descriptor)
            except OSError as exc:
                if first_error is None:
                    first_error = exc
        if first_error is not None:
            raise first_error

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def verify(self) -> None:
        opened = os.fstat(self.descriptor)
        current = self.path.stat()
        if (opened.st_dev, opened.st_ino) != (self.device, self.inode) or (
            current.st_dev,
            current.st_ino,
        ) != (self.device, self.inode):
            raise OSError("bound directory identity changed")

    def open_file(self, name: str, flags: int, mode: int = 0o600) -> int:
        if Path(name).name != name:
            raise ValueError("bound file name must be a basename")
        binary_flags = flags | getattr(os, "O_BINARY", 0)
        if os.name == "nt":
            self.verify()
            descriptor = os.open(self.path / name, binary_flags, mode)
            self.verify()
            return descriptor
        return os.open(name, binary_flags, mode, dir_fd=self.descriptor)

    def replace(self, source_name: str, target_name: str) -> None:
        if os.name == "nt":
            self.verify()
            os.replace(self.path / source_name, self.path / target_name)
            self.verify()
        else:
            os.replace(
                source_name,
                target_name,
                src_dir_fd=self.descriptor,
                dst_dir_fd=self.descriptor,
            )

    def link(self, source_name: str, target_name: str) -> None:
        if os.name == "nt":
            self.verify()
            os.link(self.path / source_name, self.path / target_name)
            self.verify()
        else:
            os.link(
                source_name,
                target_name,
                src_dir_fd=self.descriptor,
                dst_dir_fd=self.descriptor,
            )

    def unlink(self, name: str) -> None:
        if os.name == "nt":
            self.verify()
            os.unlink(self.path / name)
            self.verify()
        else:
            os.unlink(name, dir_fd=self.descriptor)

    def lstat(self, name: str) -> os.stat_result:
        if os.name == "nt":
            self.verify()
            return (self.path / name).lstat()
        return os.stat(name, dir_fd=self.descriptor, follow_symlinks=False)

    def fsync(self) -> None:
        if os.name == "nt":
            # Windows directory handles cannot be flushed without GENERIC_WRITE;
            # file handles are flushed, while directory-entry durability is unavailable.
            return
        try:
            os.fsync(self.descriptor)
        except OSError as exc:
            unsupported = {errno.EINVAL, getattr(errno, "ENOTSUP", errno.EINVAL)}
            if exc.errno in unsupported:
                return
            raise
