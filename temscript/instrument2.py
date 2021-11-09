import ctypes
from uuid import UUID
from enum import IntEnum
from enums import *


# COM constants
COINIT_MULTITHREADED = 0
CLSCTX_ALL = 0x17


_ole32 = ctypes.oledll.ole32
_ole32.CoInitializeEx(None, ctypes.c_int(COINIT_MULTITHREADED))
_oleauto = ctypes.windll.oleaut32


class IUnknown:
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
        #elif vt == VariantType.BSTR:
        #    return self._variant.bstr
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


class BaseProperty:
    __slots__ = '_get_index', '_put_index', '_name'

    def __init__(self, get_index=None, put_index=None):
        self._get_index = get_index
        self._put_index = put_index
        self._name = ''

    def __set_name__(self, owner, name):
        self._name = " '%s'" % name


class LongProperty(BaseProperty):
    __slots__ = '_get_index', '_put_index', '_name'

    def __get__(self, obj, objtype=None):
        if self._get_index is None:
            raise AttributeError("Attribute %sis not readable" % self._name)
        result = ctypes.c_long(-1)
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._get_index, "get_property")
        prototype(obj.get(), ctypes.byref(result))
        return result.value

    def __set__(self, obj, value):
        if self._put_index is None:
            raise AttributeError("Attribute %sis not writable" % self._name)
        value = int(value)
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_long)(self._put_index, "put_property")
        prototype(obj.get(), value)


class VariantBoolProperty(BaseProperty):
    def __get__(self, obj, objtype=None):
        if self._get_index is None:
            raise AttributeError("Attribute %sis not readable" % self._name)
        result = ctypes.c_short(-1)
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._get_index, "get_property")
        prototype(obj.get(), ctypes.byref(result))
        return bool(result.value)

    def __set__(self, obj, value):
        if self._put_index is None:
            raise AttributeError("Attribute %sis not writable" % self._name)
        bool_value = 0xffff if value else 0x0000
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_short)(self._put_index, "put_property")
        prototype(obj.get(), bool_value)


class DoubleProperty(BaseProperty):
    def __get__(self, obj, objtype=None):
        if self._get_index is None:
            raise AttributeError("Attribute %sis not readable" % self._name)
        result = ctypes.c_double(-1)
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._get_index, "get_property")
        prototype(obj.get(), ctypes.byref(result))
        return result.value

    def __set__(self, obj, value):
        if self._put_index is None:
            raise AttributeError("Attribute %sis not writable" % self._name)
        value = float(value)
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_double)(self._put_index, "put_property")
        prototype(obj.get(), value)


class StringProperty(BaseProperty):
    def __get__(self, obj, objtype=None):
        if self._get_index is None:
            raise AttributeError("Attribute %sis not readable" % self._name)
        result = BStr()
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._get_index, "get_property")
        prototype(obj.get(), result.byref())
        return result.value

    def __set__(self, obj, value):
        if self._put_index is None:
            raise AttributeError("Attribute %sis not writable" % self._name)
        value = BStr(str(value))
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._put_index, "put_property")
        prototype(obj.get(), BStr(value).get())


class EnumProperty(BaseProperty):
    __slots__ = '_enum_type'

    def __init__(self, enum_type, get_index=None, put_index=None):
        super(EnumProperty, self).__init__(get_index=get_index, put_index=put_index)
        self._enum_type = enum_type

    def __get__(self, obj, objtype=None):
        if self._get_index is None:
            raise AttributeError("Attribute %sis not readable" % self._name)
        result = ctypes.c_int(-1)
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._get_index, "get_property")
        prototype(obj.get(), ctypes.byref(result))
        return self._enum_type(result.value)

    def __set__(self, obj, value):
        if self._put_index is None:
            raise AttributeError("Attribute %sis not writable" % self._name)
        value = int(value)
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_long)(self._put_index, "put_property")
        prototype(obj.get(), value)

    def __set_name__(self, owner, name):
        self._name = " '%s'" % name


class Vector(IUnknown):
    IID = UUID("9851bc47-1b8c-11d3-ae0a-00a024cba50c")

    X = DoubleProperty(get_index=7, put_index=8)
    Y = DoubleProperty(get_index=9, put_index=10)


class VectorProperty(BaseProperty):
    __slots__ = '_get_prototype'

    def __init__(self, get_index, put_index=None):
        super(VectorProperty, self).__init__(get_index=get_index, put_index=put_index)
        self._get_prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(get_index, "get_property")

    def __get__(self, obj, objtype=None):
        result = Vector()
        self._get_prototype(obj.get(), result.byref())
        return result.X, result.Y

    def __set__(self, obj, value):
        if self._put_index is None:
            raise AttributeError("Attribute%s is not writable" % self._name)

        value = [float(c) for c in value]
        if len(value) != 2:
            raise ValueError("Expected two items for attribute%s." % self._name)

        result = Vector()
        self._get_prototype(obj.get(), result.byref())
        result.X = value[0]
        result.Y = value[1]
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._put_index, "put_property")
        prototype(obj.get(), result.get())


class ObjectProperty(BaseProperty):
    __slots__ = '_interface'

    def __init__(self, interface, get_index, put_index=None):
        super(ObjectProperty, self).__init__(get_index=get_index, put_index=put_index)
        self._interface = interface

    def __get__(self, obj, objtype=None):
        result = self._interface()
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._get_index, "get_property")
        prototype(obj.get(), result.byref())
        return result

    def __set__(self, obj, value):
        if self._put_index is None:
            raise AttributeError("Attribute%s is not writable" % self._name)
        if not isinstance(value, self._interface):
            raise TypeError("Expected attribute%s to be set to an instance of type %s" % (self._name, self._interface.__name__))
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._put_index, "put_property")
        prototype(obj.get(), value.get())


class CollectionProperty(BaseProperty):
    __slots__ = '_interface'

    GET_COUNT_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(7, "get_Count")
    GET_ITEM_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, VARIANT, ctypes.c_void_p)(8, "get_Item")

    def __init__(self, get_index, interface=None):
        super(CollectionProperty, self).__init__(get_index=get_index)
        if interface is None:
            interface = IUnknown
        self._interface = interface

    def __get__(self, obj, objtype=None):
        collection = IUnknown()
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._get_index, "get_property")
        prototype(obj.get(), collection.byref())

        count = ctypes.c_long(-1)
        CollectionProperty.GET_COUNT_METHOD(collection.get(), ctypes.byref(count))
        result = []

        for n in range(count.value):
            index = Variant(n, vartype=VariantType.I4)
            item = self._interface()
            CollectionProperty.GET_ITEM_METHOD(collection.get(), index.get(), item.byref())
            result.append(item)

        return result


class SafeArrayProperty(BaseProperty):
    def __get__(self, obj, objtype=None):
        result = SafeArray()
        prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(self._get_index, "get_property")
        prototype(obj.get(), result.byref())
        return result


class Projection(IUnknown):
    IID = UUID("b39c3ae1-1e41-11d3-ae0e-00a024cba50c")

    Mode = EnumProperty(ProjectionMode, get_index=10, put_index=11)
    Focus = DoubleProperty(get_index=12, put_index=13)
    Magnification = DoubleProperty(get_index=14)
    CameraLength = DoubleProperty(get_index=15)
    MagnificationIndex = LongProperty(get_index=16, put_index=17)
    CameraLengthIndex = LongProperty(get_index=18, put_index=19)
    ImageShift = VectorProperty(get_index=20, put_index=21)
    ImageBeamShift = VectorProperty(get_index=22, put_index=23)
    DiffractionShift = VectorProperty(get_index=24, put_index=25)
    DiffractionStigmator = VectorProperty(get_index=26, put_index=27)
    ObjectiveStigmator = VectorProperty(get_index=28, put_index=29)
    Defocus = DoubleProperty(get_index=30, put_index=31)
    SubModeString = StringProperty(get_index=32)
    SubMode = EnumProperty(ProjectionSubMode, get_index=33)
    SubModeMinIndex = LongProperty(get_index=34)
    SubModeMaxIndex = LongProperty(get_index=35)
    ObjectiveExcitation = DoubleProperty(get_index=36)
    ProjectionIndex = LongProperty(get_index=37, put_index=38)
    LensProgram = EnumProperty(LensProg, get_index=39, put_index=40)
    ImageRotation = DoubleProperty(get_index=41)
    DetectorShift = EnumProperty(ProjectionDetectorShift, get_index=42, put_index=43)
    DetectorShiftMode = EnumProperty(ProjDetectorShiftMode, get_index=44, put_index=45)
    ImageBeamTilt = VectorProperty(get_index=46, put_index=47)

    RESET_DEFOCUS_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT)(7, "ResetDefocus")
    NORMALIZE_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_int)(8, "Normalize")
    CHANGE_PROJECTION_INDEX_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_long)(9, "ChangeProjectionIndex")

    def ResetDefocus(self):
        Projection.RESET_DEFOCUS_METHOD(self.get())

    def Normalize(self, norm):
        Projection.NORMALIZE_METHOD(self.get(), norm)

    def ChangeProjectionIndex(self, add_val):
        Projection.CHANGE_PROJECTION_INDEX_METHOD(self.get(), add_val)


class CCDCameraInfo(IUnknown):
    IID = UUID("024ded60-b124-4514-bfe2-02c0f5c51db9")

    Name = StringProperty(get_index=7)
    Width = LongProperty(get_index=8)
    Height = LongProperty(get_index=9)
    PixelSize = VectorProperty(get_index=10)
    ShutterMode = EnumProperty(AcqShutterMode, get_index=13, put_index=14)
    _ShutterModes = SafeArrayProperty(get_index=12)
    _Binnings = SafeArrayProperty(get_index=11)

    @property
    def Binnings(self):
        return self._Binnings.as_list(int)

    @property
    def ShutterModes(self):
        return self._ShutterModes.as_list(AcqShutterMode)


class CCDAcqParams(IUnknown):
    IID = UUID("c03db779-1345-42ab-9304-95b85789163d")

    ImageSize = EnumProperty(AcqImageSize, get_index=7, put_index=8)
    ExposureTime = DoubleProperty(get_index=9, put_index=10)
    Binning = LongProperty(get_index=11, put_index=12)
    ImageCorrection = EnumProperty(AcqImageCorrection, get_index=13, put_index=14)
    ExposureMode = EnumProperty(AcqExposureMode, get_index=15, put_index=16)
    MinPreExposureTime = DoubleProperty(get_index=17)
    MaxPreExposureTime = DoubleProperty(get_index=18)
    PreExposureTime = DoubleProperty(get_index=19, put_index=20)
    MinPreExposurePauseTime = DoubleProperty(get_index=21)
    MaxPreExposurePauseTime = DoubleProperty(get_index=22)
    PreExposurePauseTime = DoubleProperty(get_index=23, put_index=24)


class CCDCamera(IUnknown):
    IID = UUID("e44e1565-4131-4937-b273-78219e090845")

    Info = ObjectProperty(CCDCameraInfo, get_index=7)
    AcqParams = ObjectProperty(CCDAcqParams, get_index=8, put_index=9)


class STEMDetectorInfo(IUnknown):
    IID = UUID("96de094b-9cdc-4796-8697-e7dd5dc3ec3f")

    Name = StringProperty(get_index=7)
    Brightness = DoubleProperty(get_index=8, put_index=9)
    Contrast = DoubleProperty(get_index=10, put_index=11)
    _Binnings = SafeArrayProperty(get_index=11)

    @property
    def Binnings(self):
        return self._Binnings.as_list(int)


class STEMAcqParams(IUnknown):
    IID = UUID("ddc14710-6152-4963-aea4-c67ba784c6b4")

    ImageSize = EnumProperty(AcqImageSize, get_index=7, put_index=8)
    DwellTime = DoubleProperty(get_index=9, put_index=10)
    Binning = LongProperty(get_index=11, put_index=12)


class STEMDetector(IUnknown):
    __slots__ = '_acquisition'

    IID = UUID("d77c0d65-a1dd-4d0a-af25-c280046a5719")

    Info = ObjectProperty(STEMDetectorInfo, get_index=7)

    def __init__(self, value=None, adopt_reference=False, acquisition=None):
        super(STEMDetector, self).__init__(value=value, adopt_reference=adopt_reference)
        self._acquisition = acquisition

    @property
    def AcqParams(self):
        import warnings
        warnings.warn("The attribute AcqParams of STEMDetector instances is deprecated. Use Acquisition.StemAcqParams instead.", warnings.DeprecationWarning)
        return self._acquisition.StemAcqParams

    @AcqParams.setter
    def AcqParams(self, value):
        import warnings
        warnings.warn("The attribute AcqParams of STEMDetector instances is deprecated. Use Acquisition.StemAcqParams instead.", warnings.DeprecationWarning)
        self._acquisition.StemAcqParams = value


class AcqImage(IUnknown):
    IID = UUID("e15f4810-43c6-489a-9e8a-588b0949e153")

    Name = StringProperty(get_index=7)
    Width = LongProperty(get_index=8)
    Height = LongProperty(get_index=9)
    Depth = LongProperty(get_index=10)
    _AsSafeArray = SafeArrayProperty(get_index=11)

    @property
    def Array(self):
        return self._AsSafeArray.as_array()


class Acquisition(IUnknown):
    IID = UUID("d6bbf89c-22b8-468f-80a1-947ea89269ce")

    ADD_ACQ_DEVICE_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(7, "AddAcqDevice")
    ADD_ACQ_DEVICE_BY_NAME_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_wchar_p)(8, "AddAcqDeviceByName")
    REMOVE_ACQ_DEVICE_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(9, "RemoveAcqDevice")
    REMOVE_ACQ_DEVICE_BY_NAME_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_wchar_p)(10, "RemoveAcqDeviceByName")
    REMOVE_ALL_ACQ_DEVICES_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT)(11, "RemoveAllAcqDevices")
    GET_DETECTORS_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(9, "get_Detectors")

    # Methods of STEMDetectors
    GET_ACQ_PARAMS_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(10, "get_AcqParams")
    PUT_ACQ_PARAMS_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(11, "put_AcqParams")

    _AcquireImages = CollectionProperty(get_index=12, interface=AcqImage)
    Cameras = CollectionProperty(get_index=13, interface=CCDCamera)
    _Detectors = CollectionProperty(get_index=14)

    def AddAcqDevice(self, device):
        if not isinstance(device, (STEMDetector, CCDCamera)):
            raise TypeError("Expected device to be instance of types STEMDetector or CCDCamera")
        Acquisition.ADD_ACQ_DEVICE_METHOD(self.get(), device.get())

    def AddAcqDeviceByName(self, name):
        name_bstr = BStr(name)
        Acquisition.ADD_ACQ_DEVICE_BY_NAME_METHOD(self.get(), name_bstr.get())

    def RemoveAcqDevice(self, device):
        if not isinstance(device, (STEMDetector, CCDCamera)):
            raise TypeError("Expected device to be instance of types STEMDetector or CCDCamera")
        Acquisition.REMOVE_ACQ_DEVICE_METHOD(self.get(), device.get())

    def RemoveAcqDeviceByName(self, name):
        name_bstr = BStr(name)
        Acquisition.REMOVE_ACQ_DEVICE_BY_NAME_METHOD(self.get(), name_bstr.get())

    def RemoveAllAcqDevices(self):
        Acquisition.REMOVE_ALL_ACQ_DEVICES_METHOD(self.get())

    def AcquireImages(self):
        return self._AcquireImages

    @property
    def Detectors(self):
        collection = self._Detectors
        return [STEMDetector(item, acquisition=self) for item in collection]

    @property
    def StemAcqParams(self):
        collection = IUnknown()
        Acquisition.GET_DETECTORS_METHOD(self.get(), collection.byref())
        params = STEMAcqParams()
        Acquisition.GET_ACQ_PARAMS_METHOD(collection.get(), params.byref())
        return params

    @StemAcqParams.setter
    def StemAcqParams(self, value):
        if not isinstance(value, STEMAcqParams):
            raise TypeError("Expected attribute AcqParams to be set to an instance of type STEMAcqParams")
        collection = IUnknown()
        Acquisition.GET_DETECTORS_METHOD(self.get(), collection.byref())
        Acquisition.PUT_ACQ_PARAMS_METHOD(collection.get(), value.get())


class Instrument(IUnknown):
    IID = UUID("bc0a2b11-10ff-11d3-ae00-00a024cba50c")

    AutoNormalizeEnabled = VariantBoolProperty(get_index=8, put_index=9)
    Projection = ObjectProperty(Projection, get_index=17)
    Acquisition = ObjectProperty(Acquisition, get_index=24)

    NORMALIZE_ALL_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT)(7, "NormalizeAll")

    # 10: virtual HRESULT __stdcall raw_ReturnError ( /*[in]*/ enum TEMScriptingError TE ) = 0;
    GET_VECTOR_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(11, "get_Vector")
    # 12: virtual HRESULT __stdcall get_StagePosition ( /*[out,retval]*/ IDispatch * * pStp ) = 0;
    # 13: virtual HRESULT __stdcall get_Vacuum ( /*[out,retval]*/ struct Vacuum * * pVac ) = 0;
    # 14: virtual HRESULT __stdcall get_Camera ( /*[out,retval]*/ struct Camera * * pCamera ) = 0;
    # 15: virtual HRESULT __stdcall get_Stage ( /*[out,retval]*/ struct Stage * * pStage ) = 0;
    # 16: virtual HRESULT __stdcall get_Illumination ( /*[out,retval]*/ struct Illumination * * pI ) = 0;
    GET_PROJECTION_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(17, "get_Projection")
    # 18: virtual HRESULT __stdcall get_Gun ( /*[out,retval]*/ struct Gun * * pG ) = 0;
    GET_USER_BUTTONS_METHOD = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(19, "get_UserButtons")

    # 20: virtual HRESULT __stdcall get_AutoLoader ( /*[out,retval]*/ struct AutoLoader * * pAL ) = 0;
    # 21: virtual HRESULT __stdcall get_TemperatureControl ( /*[out,retval]*/ struct TemperatureControl * * pTC ) = 0;
    # 22: virtual HRESULT __stdcall get_BlankerShutter ( /*[out,retval]*/ struct BlankerShutter * * pBS ) = 0;
    # 23: virtual HRESULT __stdcall get_InstrumentModeControl ( /*[out,retval]*/ struct InstrumentModeControl * * pIMC ) = 0;
    # 24: virtual HRESULT __stdcall get_Acquisition ( /*[out,retval]*/ struct Acquisition * * pIAcq ) = 0;
    # 25: virtual HRESULT __stdcall get_Configuration ( /*[out,retval]*/ struct Configuration * * pIConfig ) = 0;


CLSID_INSTRUMENT = UUID('02CDC9A1-1F1D-11D3-AE11-00A024CBA50C')


def GetInstrument():
    """Returns Instrument instance."""
    instrument = co_create_instance(CLSID_INSTRUMENT, CLSCTX_ALL, Instrument)
    return instrument


