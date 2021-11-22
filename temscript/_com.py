import ctypes
from uuid import UUID
from enum import IntEnum

__all__ = 'UUID', 'CLSCTX_ALL', 'IUnknown', 'co_create_instance', 'SafeArray', 'BStr', 'Variant', 'VARIANT', 'VariantType'

# COM constants
COINIT_MULTITHREADED = 0
CLSCTX_ALL = 0x17


class IUnknown:
    """Base class for COM interface classes, adapter for IUnknown methods"""
    __slots__ = '_ptr'

    IID = UUID('00000000-0000-0000-C000-000000000046')

    QUERYINTERFACE_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_char_p, ctypes.c_void_p)(0, "QueryInterface")
    ADDREF_METHOD = ctypes.WINFUNCTYPE(ctypes.c_int)(1, "AddRef")
    RELEASE_METHOD = ctypes.WINFUNCTYPE(ctypes.c_int)(2, "Release")

    def __del__(self):
        if self._ptr:
            IUnknown.RELEASE_METHOD(self._ptr)
        self._ptr = None

    def __init__(self, value=None, adopt_reference=False):
        self._ptr = ctypes.c_void_p()
        self.reset(value=value, adopt_reference=adopt_reference)

    def reset(self, value=None, adopt_reference=False):
        if value is None:
            value = ctypes.c_void_p()
        elif isinstance(value, ctypes._SimpleCData):
            value = ctypes.c_void_p(value.value)
        elif isinstance(value, IUnknown):
            value = ctypes.c_void_p(value.get().value)
        else:
            value = ctypes.c_void_p(int(value))

        if value and not adopt_reference:
            IUnknown.ADDREF_METHOD(value)

        old = self._ptr
        self._ptr = value

        if old:
            IUnknown.RELEASE_METHOD(old)

    def query_interface(self, interface, iid=None):
        if not self._ptr:
            raise ValueError("Calling method of NULL pointer.")
        if iid is None:
            iid = interface.IID
        if not isinstance(iid, UUID):
            iid = UUID(iid)

        obj = interface()
        IUnknown.QUERYINTERFACE_METHOD(self._ptr, iid.bytes_le, obj.byref())

        return obj

    def get(self):
        return self._ptr

    def __bool__(self):
        return bool(self._ptr)

    def byref(self):
        return ctypes.byref(self._ptr)


def co_create_instance(clsid, clsctx, interface=None, iid=None):
    if interface is None:
        interface = IUnknown
    if not isinstance(clsid, UUID):
        clsid = UUID(clsid)
    if iid is None:
        iid = interface.IID
    if not isinstance(iid, UUID):
        iid = UUID(iid)

    obj = interface()
    _ole32.CoCreateInstance(clsid.bytes_le, None, ctypes.c_uint(clsctx), iid.bytes_le, obj.byref())

    return obj


class BStr:
    __slots__ = '_ptr'

    def __del__(self):
        if self._ptr:
            _oleauto.SysFreeString(self._ptr)

    def __init__(self, text=None):
        if text is not None:
            self._ptr = ctypes.c_wchar_p(_oleauto.SysAllocString(ctypes.c_wchar_p(text)))
            if not self._ptr:
                raise ValueError("SysAllocString returned NULL.")
        else:
            self._ptr = ctypes.c_wchar_p()

    def __len__(self):
        return _oleauto.SysStringLen(self._ptr)

    def __str__(self):
        return self.value

    def byref(self):
        return ctypes.byref(self._ptr)

    def get(self):
        return self._ptr

    @property
    def value(self):
        return str(self._ptr.value)


class VariantType(IntEnum):
    EMPTY = 0
    NULL = 1
    I2 = 2  # iVal
    I4 = 3  # lVal
    R4 = 4  # fltVal
    R8 = 5  # dblVal
    BSTR = 8  # bstr
    BOOL = 11  # bool(uiVal)
    I1 = 16  # cVal
    UI1 = 17  # bVal
    UI2 = 18  # uiVal
    UI4 = 19  # ulVal
    I8 = 20  # llVal
    UI8 = 21  # ullVal
    INT = 22  # intVal
    UINT = 23  # uintVal
    SAFEARRAY = 27  # TODO


class VARIANT(ctypes.Structure):
    class _ValueUnion(ctypes.Union):
        _fields_ = [('llVal', ctypes.c_longlong),
                    ('ullVal', ctypes.c_ulonglong),
                    ('lVal', ctypes.c_long),
                    ('ulVal', ctypes.c_ulong),
                    ('iVal', ctypes.c_short),
                    ('uiVal', ctypes.c_ushort),
                    ('intVal', ctypes.c_int),
                    ('uintVal', ctypes.c_uint),
                    ('fltVal', ctypes.c_float),
                    ('dblVal', ctypes.c_double),
                    ('cVal', ctypes.c_byte),
                    ('bVal', ctypes.c_ubyte),
                    ('bstr', ctypes.c_wchar_p)]

    _anonymous_ = ('value',)
    _fields_ = [('vt', ctypes.c_ushort),
                ('wReserved1', ctypes.c_ushort),
                ('wReserved2', ctypes.c_ushort),
                ('wReserved3', ctypes.c_ushort),
                ('value', _ValueUnion)]


class Variant:
    __slots__ = '_variant'

    def __del__(self):
        _oleauto.VariantClear(ctypes.byref(self._variant))

    def __init__(self, value=None, vartype=None):
        self._variant = VARIANT()
        _oleauto.VariantInit(ctypes.byref(self._variant))

        # Determine variant type if needed
        if vartype is not None:
            vartype = VariantType(vartype)
        elif value is None:
            vartype = VariantType.NULL
        elif isinstance(value, int):
            vartype = VariantType.I4            # TODO: Check range
        elif isinstance(value, float):
            vartype = VariantType.R8            # TODO: Check range
        elif isinstance(value, bool):
            vartype = VariantType.BOOL
        else:
            raise TypeError("Unsupported value type: %s" % type(value).__name__)

        # Set value
        if (vartype == VariantType.EMPTY) or (vartype == VariantType.NULL):
            pass
        elif vartype == VariantType.I2:
            self._variant.iVal = int(value)
        elif vartype == VariantType.I4:
            self._variant.lVal = int(value)
        elif vartype == VariantType.R4:
            self._variant.fltVal = float(value)
        elif vartype == VariantType.R8:
            self._variant.dblVal = float(value)
        elif vartype == VariantType.BOOL:
            self._variant.uiVal = 0xffff if value else 0x0000
        elif vartype == VariantType.I1:
            self._variant.cVal = int(value)
        elif vartype == VariantType.UI1:
            self._variant.bVal = int(value)
        elif vartype == VariantType.UI2:
            self._variant.uiVal = int(value)
        elif vartype == VariantType.UI4:
            self._variant.ulVal = int(value)
        elif vartype == VariantType.I8:
            self._variant.llVal = int(value)
        elif vartype == VariantType.UI8:
            self._variant.ullVal = int(value)
        elif vartype == VariantType.INT:
            self._variant.intVal = int(value)
        elif vartype == VariantType.UINT:
            self._variant.uintVal = int(value)
        else:
            raise ValueError("Unsupported variant type: %s" % vartype)
        self._variant.vt = vartype

    def byref(self):
        return ctypes.byref(self._variant)

    def get(self):
        return self._variant

    @property
    def vartype(self):
        return VariantType(self._variant.vt)

    @property
    def value(self):
        t = self.vartype
        if t == VariantType.NULL:
            return None
        elif t == VariantType.I2:
            return self._variant.iVal
        elif t == VariantType.I4:
            return self._variant.lVal
        elif t == VariantType.R4:
            return self._variant.fltVal
        elif t == VariantType.R8:
            return self._variant.dblVal
        elif t == VariantType.BOOL:
            return bool(self._variant.uiVal)
        elif t == VariantType.I1:
            return self._variant.cVal
        elif t == VariantType.UI1:
            return self._variant.bVal
        elif t == VariantType.UI2:
            return self._variant.uiVal
        elif t == VariantType.UI4:
            return self._variant.ulVal
        elif t == VariantType.I8:
            return self._variant.llVal
        elif t == VariantType.UI8:
            return self._variant.ullVal
        elif t == VariantType.INT:
            return self._variant.intVal
        elif t == VariantType.UINT:
            return self._variant.uintVal
        elif t == VariantType.BSTR:
            return self._variant.bstr
        else:
            raise ValueError("Unexpected Variant type")


class SafeArray:
    __slots__ = '_ptr'

    CTYPE_FOR_VARTYPE = {
        VariantType.I1: ctypes.c_byte,
        VariantType.I2: ctypes.c_short,
        VariantType.I4: ctypes.c_long,      # long is always 4 byte in MSVC
        VariantType.I8: ctypes.c_longlong,
        VariantType.UI1: ctypes.c_ubyte,
        VariantType.UI2: ctypes.c_ushort,
        VariantType.UI4: ctypes.c_ulong,    # long is always 4 byte in MSVC
        VariantType.UI8: ctypes.c_ulonglong,
        VariantType.R4: ctypes.c_float,
        VariantType.R8: ctypes.c_double,
        VariantType.INT: ctypes.c_int,
        VariantType.UINT: ctypes.c_uint
    }

    def __del__(self):
        _oleauto.SafeArrayDestroy(self._ptr)

    def __init__(self):
        self._ptr = ctypes.c_void_p()

    def byref(self):
        return ctypes.byref(self._ptr)

    def get(self):
        return self._ptr

    def get_vartype(self):
        vt = ctypes.c_int()
        if _oleauto.SafeArrayGetVartype(self._ptr, ctypes.byref(vt)) < 0:
            raise ValueError("Error retrieving vartype from SafeArray.")
        return VariantType(vt.value)

    def get_ctype(self):
        return SafeArray.CTYPE_FOR_VARTYPE[self.get_vartype()]

    def get_dim(self):
        return _oleauto.SafeArrayGetDim(self._ptr)

    def get_lower_bound(self, axis):
        lower = ctypes.c_long(-1)
        if _oleauto.SafeArrayGetLBound(self._ptr, ctypes.c_int(axis + 1), ctypes.byref(lower)) < 0:
            raise ValueError("Error retrieving lower bound from SafeArray.")
        return lower.value

    def get_upper_bound(self, axis):
        upper = ctypes.c_long(-1)
        if _oleauto.SafeArrayGetUBound(self._ptr, ctypes.c_int(axis + 1), ctypes.byref(upper)) < 0:
            raise ValueError("Error retrieving lower bound from SafeArray.")
        return upper.value

    @staticmethod
    def _forward(arg):
        return arg

    def as_list(self, cast=None):
        if cast is None:
            cast = SafeArray._forward

        ndim = self.get_dim()
        size = 1
        for n in range(ndim):
            lower = self.get_lower_bound(n)
            upper = self.get_upper_bound(n)
            size *= upper - lower + 1

        ct = self.get_ctype()
        ptr = ctypes.POINTER(ct)()
        if _oleauto.SafeArrayAccessData(self._ptr, ctypes.byref(ptr)) < 0:
            raise ValueError("Error accessing SafeArray's data.")
        try:
            result = [cast(ptr[n]) for n in range(size)]
        finally:
            _oleauto.SafeArrayUnaccessData(self._ptr)

        return result

    def as_array(self):
        import numpy as np

        ndim = self.get_dim()
        shape = []
        for n in range(ndim):
            lower = self.get_lower_bound(ndim - n - 1)
            upper = self.get_upper_bound(ndim - n - 1)
            shape.append(upper - lower + 1)
        shape = tuple(shape)

        ct = self.get_ctype()
        ptr = ctypes.POINTER(ct)()
        if _oleauto.SafeArrayAccessData(self._ptr, ctypes.byref(ptr)) < 0:
            raise ValueError("Error accessing SafeArray's data.")
        try:
            result = np.ctypeslib.as_array(ptr, shape=shape).copy()
        finally:
            _oleauto.SafeArrayUnaccessData(self._ptr)

        return result


_ole32 = ctypes.oledll.ole32
_ole32.CoInitializeEx(None, ctypes.c_int(COINIT_MULTITHREADED))
_oleauto = ctypes.windll.oleaut32
