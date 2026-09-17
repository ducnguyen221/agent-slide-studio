from __future__ import annotations

from dataclasses import dataclass
import ctypes
import errno
import os
from pathlib import Path
import stat
from typing import Self


class UnsafeFileError(OSError):
    pass


def _safe_identity(info: os.stat_result, *, directory: bool = False) -> None:
    marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if (
        bool(getattr(info, "st_file_attributes", 0) & marker)
        or not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode))
        or (not directory and info.st_nlink != 1)
    ):
        raise UnsafeFileError("linked or unsafe filesystem identity")


def _windows_open(path: Path, *, access: int, creation: int, directory: bool = False) -> int:
    import msvcrt

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    create.restype = ctypes.c_void_p
    # No FILE_SHARE_DELETE: keep the opened entry pinned until its handle closes.
    handle = create(str(path), access, 0x1 | 0x2, None, creation,
                    0x00200000 | (0x02000000 if directory else 0), None)
    if handle in (None, ctypes.c_void_p(-1).value):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return msvcrt.open_osfhandle(int(handle), os.O_BINARY)
    except BaseException:
        close = kernel.CloseHandle
        close.argtypes = [ctypes.c_void_p]
        close(handle)
        raise


def _windows_create_directory_at(
    parent_descriptor: int, name: str, *, allow_delete: bool
) -> int:
    """Atomically create and bind a directory relative to a pinned parent handle."""
    import msvcrt

    class UnicodeString(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ushort),
            ("maximum_length", ctypes.c_ushort),
            ("buffer", ctypes.c_wchar_p),
        ]

    class ObjectAttributes(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_uint32),
            ("root_directory", ctypes.c_void_p),
            ("object_name", ctypes.POINTER(UnicodeString)),
            ("attributes", ctypes.c_uint32),
            ("security_descriptor", ctypes.c_void_p),
            ("security_quality_of_service", ctypes.c_void_p),
        ]

    class IoStatusBlock(ctypes.Structure):
        _fields_ = [("status", ctypes.c_void_p), ("information", ctypes.c_size_t)]

    name_buffer = ctypes.create_unicode_buffer(name)
    object_name = UnicodeString(
        length=len(name.encode("utf-16-le")),
        maximum_length=ctypes.sizeof(name_buffer),
        buffer=ctypes.cast(name_buffer, ctypes.c_wchar_p),
    )
    attributes = ObjectAttributes(
        length=ctypes.sizeof(ObjectAttributes),
        root_directory=ctypes.c_void_p(msvcrt.get_osfhandle(parent_descriptor)),
        object_name=ctypes.pointer(object_name),
        attributes=0x40,
        security_descriptor=None,
        security_quality_of_service=None,
    )
    io_status = IoStatusBlock()
    handle = ctypes.c_void_p()
    ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
    create = ntdll.NtCreateFile
    create.argtypes = [
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_uint32,
        ctypes.POINTER(ObjectAttributes),
        ctypes.POINTER(IoStatusBlock),
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
    ]
    create.restype = ctypes.c_long
    desired_access = 0x0001 | 0x0020 | 0x0080 | 0x100000
    if allow_delete:
        desired_access |= 0x10000
    status = create(
        ctypes.byref(handle),
        desired_access,
        ctypes.byref(attributes),
        ctypes.byref(io_status),
        None,
        0x80,
        0x1 | 0x2,
        2,
        0x00000001 | 0x00000020 | 0x00200000,
        None,
        0,
    )
    if status < 0:
        to_dos_error = ntdll.RtlNtStatusToDosError
        to_dos_error.argtypes = [ctypes.c_long]
        to_dos_error.restype = ctypes.c_uint32
        raise ctypes.WinError(to_dos_error(status))
    try:
        return msvcrt.open_osfhandle(int(handle.value), os.O_RDONLY)
    except BaseException:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel.CloseHandle.restype = ctypes.c_int
        kernel.CloseHandle(handle)
        raise


def _windows_delete_by_handle(descriptor: int) -> None:
    import msvcrt

    class DispositionInfo(ctypes.Structure):
        _fields_ = [("delete", ctypes.c_ubyte)]

    info = DispositionInfo(1)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    dispose = kernel.SetFileInformationByHandle
    dispose.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    dispose.restype = ctypes.c_int
    if not dispose(
        msvcrt.get_osfhandle(descriptor), 4, ctypes.byref(info), ctypes.sizeof(info)
    ):
        raise ctypes.WinError(ctypes.get_last_error())


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
                        raise UnsafeFileError(
                            "refusing to bind a reparse-point directory"
                        )
                    is_leaf = item == path
                    share = 0x1 | 0x2
                    handle = create_file(
                        str(item), 0x80 | (0x10000 if allow_delete and is_leaf else 0),
                        share, None, 3, 0x02000000 | 0x00200000, None
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
                    opened = os.fstat(descriptor)
                    _safe_identity(opened, directory=True)
                    current = item.lstat()
                    _safe_identity(current, directory=True)
                    if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino) or (
                        opened.st_dev, opened.st_ino
                    ) != (current.st_dev, current.st_ino):
                        raise UnsafeFileError("directory identity changed while binding")
            except BaseException:
                for guard in reversed(descriptors):
                    os.close(guard)
                raise
            descriptor = descriptors[-1]
            guards = descriptors[:-1]
        else:
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
            descriptors = []
            try:
                for part in (path.anchor, *path.parts[1:]):
                    descriptor = os.open(part, flags, dir_fd=descriptors[-1] if descriptors else None)
                    descriptors.append(descriptor)
                    _safe_identity(os.fstat(descriptor), directory=True)
            except BaseException:
                for descriptor in reversed(descriptors):
                    os.close(descriptor)
                raise
            descriptor, guards = descriptors[-1], descriptors[:-1]
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISDIR(info.st_mode):
                raise NotADirectoryError(path)
            current = path.lstat()
            _safe_identity(current, directory=True)
            if (info.st_dev, info.st_ino) != (current.st_dev, current.st_ino):
                raise UnsafeFileError("directory identity changed while binding")
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

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        try:
            self.close()
        except OSError:
            if exc_type is None:
                raise

    def verify(self) -> None:
        opened = os.fstat(self.descriptor)
        current = self.path.lstat()
        _safe_identity(opened, directory=True)
        _safe_identity(current, directory=True)
        if (opened.st_dev, opened.st_ino) != (self.device, self.inode) or (
            current.st_dev,
            current.st_ino,
        ) != (self.device, self.inode):
            raise UnsafeFileError("bound directory identity changed")

    def open_file(self, name: str, flags: int, mode: int = 0o600) -> int:
        if not name or name in {".", ".."} or Path(name).name != name or ":" in name:
            raise ValueError("bound file name must be a basename")
        self.verify()
        try:
            before = self.lstat(name)
            _safe_identity(before)
        except FileNotFoundError:
            before = None
        binary_flags = (flags & ~os.O_TRUNC) | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        if os.name == "nt":
            access = 0x80000000
            if flags & (os.O_WRONLY | os.O_RDWR):
                access |= 0x40000000
            creation = 1 if flags & os.O_EXCL else (4 if flags & os.O_CREAT else 3)
            descriptor = _windows_open(self.path / name, access=access, creation=creation)
        else:
            descriptor = os.open(name, binary_flags, mode, dir_fd=self.descriptor)
        try:
            self.verify_file(name, descriptor)
            opened = os.fstat(descriptor)
            if before is not None and (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
                raise UnsafeFileError("file identity changed while opening")
            if flags & os.O_TRUNC:
                os.ftruncate(descriptor, 0)
            if flags & os.O_APPEND:
                os.lseek(descriptor, 0, os.SEEK_END)
            return descriptor
        except BaseException:
            os.close(descriptor)
            raise

    def verify_file(self, name: str, descriptor: int) -> None:
        self.verify()
        opened, current = os.fstat(descriptor), self.lstat(name)
        _safe_identity(opened)
        _safe_identity(current)
        if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
            raise UnsafeFileError("file identity changed")

    def child(
        self,
        name: str,
        *,
        create: bool = False,
        exclusive: bool = False,
        allow_delete: bool = False,
        expected: os.stat_result | None = None,
    ) -> Self:
        if not name or name in {".", ".."} or Path(name).name != name or ":" in name:
            raise ValueError("bound directory name must be a basename")
        self.verify()
        descriptor: int | None = None
        try:
            if create and exclusive and os.name == "nt":
                descriptor = _windows_create_directory_at(
                    self.descriptor, name, allow_delete=allow_delete
                )
            elif create:
                try:
                    if os.name == "nt":
                        os.mkdir(self.path / name, 0o700)
                    else:
                        os.mkdir(name, 0o700, dir_fd=self.descriptor)
                except FileExistsError:
                    if exclusive:
                        raise
            before = self.lstat(name)
            _safe_identity(before, directory=True)
            if expected is not None:
                _safe_identity(expected, directory=True)
                if (before.st_dev, before.st_ino) != (expected.st_dev, expected.st_ino):
                    raise UnsafeFileError("child directory identity changed")
            if descriptor is None and os.name == "nt":
                descriptor = _windows_open(
                    self.path / name,
                    access=0x80 | (0x10000 if allow_delete else 0),
                    creation=3,
                    directory=True,
                )
            elif descriptor is None:
                descriptor = os.open(
                    name,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                    dir_fd=self.descriptor,
                )
            opened = os.fstat(descriptor)
            _safe_identity(opened, directory=True)
            if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino) or (
                expected is not None
                and (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino)
            ):
                raise UnsafeFileError("child directory identity changed")
            child = type(self)(self.path / name, descriptor, opened.st_dev, opened.st_ino, [])
            child.verify()
            return child
        except BaseException as primary_error:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except BaseException as close_error:
                    primary_error.add_note(
                        "child descriptor close failed: "
                        + type(close_error).__name__
                    )
            raise

    def rename_noreplace(self, target: Path) -> None:
        """Rename this directory through its pinned Windows handle, never a source name."""
        self.verify()
        if os.name != "nt":
            raise OSError(errno.ENOTSUP, "identity-bound directory promotion is unavailable")
        import msvcrt

        class RenameInfo(ctypes.Structure):
            _fields_ = [
                ("flags", ctypes.c_uint32),
                ("root", ctypes.c_void_p),
                ("length", ctypes.c_uint32),
                ("name", ctypes.c_wchar * 1),
            ]

        encoded = str(target.absolute()).encode("utf-16-le")
        # Include the structure's trailing WCHAR/padding in dwBufferSize. Passing
        # only `name.offset + len(encoded)` lets some filesystems read beyond the
        # caller-owned buffer and append unrelated UTF-16 code units.
        size = ctypes.sizeof(RenameInfo) + len(encoded)
        buffer = ctypes.create_string_buffer(size)
        info = RenameInfo.from_buffer(buffer)
        info.flags, info.root, info.length = 0, None, len(encoded)
        ctypes.memmove(ctypes.addressof(buffer) + RenameInfo.name.offset, encoded, len(encoded))
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        rename = kernel.SetFileInformationByHandle
        rename.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
        rename.restype = ctypes.c_int
        # FileRenameInfoEx (22) applies the zero-flags no-replace contract
        # atomically even when another handle has a rename pending.
        if not rename(msvcrt.get_osfhandle(self.descriptor), 22, buffer, size):
            raise ctypes.WinError(ctypes.get_last_error())
        opened = os.fstat(self.descriptor)
        _safe_identity(opened, directory=True)
        if (opened.st_dev, opened.st_ino) != (self.device, self.inode):
            raise UnsafeFileError("directory identity changed during promotion")
        self.path = target.absolute()

    def remove_tree(self) -> None:
        """Delete this exact pinned Windows directory and its safe descendants."""
        if os.name != "nt":
            raise OSError(errno.ENOTSUP, "handle-bound tree removal is unavailable")
        self.verify()
        with os.scandir(self.path) as entries:
            names = [entry.name for entry in entries]
        self.verify()
        for name in names:
            info = self.lstat(name)
            marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
            if bool(getattr(info, "st_file_attributes", 0) & marker):
                raise UnsafeFileError("refusing to remove a reparse-point entry")
            if stat.S_ISDIR(info.st_mode):
                child = self.child(name, allow_delete=True, expected=info)
                try:
                    child.remove_tree()
                finally:
                    child.close()
            elif stat.S_ISREG(info.st_mode):
                self._unlink_file_by_identity(name, info)
            else:
                raise UnsafeFileError("refusing to remove an unsafe entry")
        self.verify()
        _windows_delete_by_handle(self.descriptor)

    def _unlink_file_by_identity(self, name: str, expected: os.stat_result) -> None:
        descriptor = _windows_open(
            self.path / name, access=0x10000, creation=3, directory=False
        )
        try:
            opened = os.fstat(descriptor)
            _safe_identity(opened)
            current = self.lstat(name)
            _safe_identity(current)
            expected_id = (expected.st_dev, expected.st_ino)
            if (opened.st_dev, opened.st_ino) != expected_id or (
                current.st_dev,
                current.st_ino,
            ) != expected_id:
                raise UnsafeFileError("file identity changed during removal")
            _windows_delete_by_handle(descriptor)
        finally:
            os.close(descriptor)

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
