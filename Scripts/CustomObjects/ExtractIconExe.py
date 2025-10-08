"""
Code from pythonassets.com : https://pythonassets.com/posts/extract-icon-from-executable-file-windows/
And modified by gemini to not extract hard pixel but do this dynamically
"""

from ctypes import Array, byref, c_char, memset, sizeof
from ctypes import c_int, c_void_p, POINTER
from ctypes.wintypes import *
from enum import Enum
import ctypes

BI_RGB = 0
DIB_RGB_COLORS = 0


class ICONINFO(ctypes.Structure):
    _fields_ = [
        ("fIcon", BOOL),
        ("xHotspot", DWORD),
        ("yHotspot", DWORD),
        ("hbmMask", HBITMAP),
        ("hbmColor", HBITMAP)
    ]


class RGBQUAD(ctypes.Structure):
    _fields_ = [
        ("rgbBlue", BYTE),
        ("rgbGreen", BYTE),
        ("rgbRed", BYTE),
        ("rgbReserved", BYTE),
    ]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", DWORD),
        ("biWidth", LONG),
        ("biHeight", LONG),
        ("biPlanes", WORD),
        ("biBitCount", WORD),
        ("biCompression", DWORD),
        ("biSizeImage", DWORD),
        ("biXPelsPerMeter", LONG),
        ("biYPelsPerMeter", LONG),
        ("biClrUsed", DWORD),
        ("biClrImportant", DWORD)
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", RGBQUAD * 1),
    ]


class BITMAP(ctypes.Structure):
    _fields_ = [
        ("bmType", LONG),
        ("bmWidth", LONG),
        ("bmHeight", LONG),
        ("bmWidthBytes", LONG),
        ("bmPlanes", WORD),
        ("bmBitsPixel", WORD),
        ("bmBits", LPVOID),
    ]


shell32 = ctypes.WinDLL("shell32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

gdi32.CreateCompatibleDC.argtypes = [HDC]
gdi32.CreateCompatibleDC.restype = HDC
gdi32.GetDIBits.argtypes = [
    HDC, HBITMAP, UINT, UINT, LPVOID, c_void_p, UINT
]
gdi32.GetDIBits.restype = c_int
gdi32.DeleteObject.argtypes = [HGDIOBJ]
gdi32.DeleteObject.restype = BOOL
gdi32.GetObjectW.argtypes = [HANDLE, c_int, LPVOID]
gdi32.GetObjectW.restype = c_int
shell32.ExtractIconExW.argtypes = [
    LPCWSTR, c_int, POINTER(HICON), POINTER(HICON), UINT
]
shell32.ExtractIconExW.restype = UINT
user32.GetIconInfo.argtypes = [HICON, POINTER(ICONINFO)]
user32.GetIconInfo.restype = BOOL
user32.DestroyIcon.argtypes = [HICON]
user32.DestroyIcon.restype = BOOL


class IconSize(Enum):
    SMALL = 1
    LARGE = 2


def extract_icon(filename: str, size: IconSize) -> tuple[HICON, ICONINFO, Array[c_char], int, int]:
    """
    Extract the icon from the specified `filename`, which might be
    either an executable or an `.ico` file.
    """
    hicon: HICON = HICON()
    extracted_icons: UINT = shell32.ExtractIconExW(
        filename,
        0,
        byref(hicon) if size == IconSize.LARGE else None,
        byref(hicon) if size == IconSize.SMALL else None,
        1
    )
    if extracted_icons != 1:
        raise ctypes.WinError()

    icon_info: ICONINFO = ICONINFO()
    if not user32.GetIconInfo(hicon, byref(icon_info)):
        user32.DestroyIcon(hicon)
        raise ctypes.WinError()

    # Get bitmap info to determine dimensions
    bmp = BITMAP()
    gdi32.GetObjectW(icon_info.hbmColor, sizeof(BITMAP), byref(bmp))
    width, height = bmp.bmWidth, bmp.bmHeight

    dc: HDC = user32.GetDC(None)

    bmi: BITMAPINFO = BITMAPINFO()
    memset(byref(bmi), 0, sizeof(bmi))
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height  # top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB

    bits = ctypes.create_string_buffer(width * height * 4)

    copied_lines = gdi32.GetDIBits(
        dc, icon_info.hbmColor, 0, height, bits, byref(bmi), DIB_RGB_COLORS
    )

    user32.ReleaseDC(None, dc)

    if copied_lines == 0:
        if icon_info.hbmColor: gdi32.DeleteObject(icon_info.hbmColor)
        if icon_info.hbmMask: gdi32.DeleteObject(icon_info.hbmMask)
        user32.DestroyIcon(hicon)
        raise ctypes.WinError()

    return hicon, icon_info, bits, width, height
