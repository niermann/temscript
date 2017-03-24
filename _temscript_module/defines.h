#ifndef DEFINES_INC
#define DEFINES_INC

#include "temscript.h"

/** 
 * Publically declare interface wrapper <cls>, its creator, and accessor.
 */
#define DECLARE_WRAPPER(cls, iface_cls) \
    struct cls { \
        PyObject_HEAD \
        PyObject*   weakRefList; \
        iface_cls*  iface; \
    }; \
    extern PyTypeObject cls##_Type; \
    PyObject* cls##_create(iface_cls* iface); \
    iface_cls* cls##_query(PyObject* self);

/** 
 * Create interface wrapper and define creator <cls>_create(<iface_cls>*),
 * COM object query <iface_cls>* <cls>_query(<cls>*) and destructor <cls>_dealloc.
 * getset and methods are getset and methods lists.
 */
#define IMPLEMENT_WRAPPER(cls, iface_cls, getset, methods) \
    static void cls##_dealloc(cls* self) \
    { \
        DEBUGF(#cls "(%p): dealloc\n", self); \
        if (self->weakRefList != NULL) \
            PyObject_ClearWeakRefs((PyObject*)self); \
        self->iface->Release(); \
        self->iface = NULL; \
        Py_TYPE(self)->tp_free((PyObject*)self); \
    } \
    PyObject* cls##_create(iface_cls* iface) \
    { \
        cls* self = PyObject_NEW(cls, &cls##_Type); \
        if (self) { \
            self->iface = iface; \
            self->weakRefList = NULL; \
            DEBUGF(#cls "(%p): create(%p)\n", self, iface); \
        } \
        return (PyObject *)self; \
    } \
    iface_cls* cls##_query(PyObject* self) \
    { \
        if (!self || !PyObject_TypeCheck(self, &cls##_Type)) \
            return NULL; \
        return reinterpret_cast<cls*>(self)->iface; \
    } \
    PyTypeObject cls##_Type = { \
        PyVarObject_HEAD_INIT(NULL, 0) \
        "temscript." #cls,                  /*tp_name*/         \
        sizeof(cls),                        /*tp_basicsize*/    \
        0,                                  /*tp_itemsize*/     \
        (destructor)cls##_dealloc,          /*tp_dealloc*/      \
        0,                                  /*tp_print*/        \
        0,                                  /*tp_getattr*/      \
        0,                                  /*tp_setattr*/      \
        0,                                  /*tp_compare*/      \
        0,                                  /*tp_repr*/         \
        0,                                  /*tp_as_number*/    \
        0,                                  /*tp_as_sequence*/  \
        0,                                  /*tp_as_mapping*/   \
        0,                                  /*tp_hash */        \
        0,                                  /*tp_call*/         \
        0,                                  /*tp_str*/          \
        0,                                  /*tp_getattro*/     \
        0,                                  /*tp_setattro*/     \
        0,                                  /*tp_as_buffer*/    \
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /*tp_flags*/    \
        0,                                  /* tp_doc */        \
        0,                                  /* tp_traverse */   \
        0,                                  /* tp_clear */      \
        0,                                  /* tp_richcompare */ \
        offsetof(cls, weakRefList),         /* tp_weaklistoffset */ \
        0,                                  /* tp_iter */       \
        0,                                  /* tp_iternext */   \
        methods,                            /* tp_methods */    \
        0,                                  /* tp_members */    \
        getset,                             /* tp_getset */     \
        0,                                  /* tp_base */       \
        0,                                  /* tp_dict */       \
        0,                                  /* tp_descr_get */  \
        0,                                  /* tp_descr_set */  \
        0,                                  /* tp_dictoffset */ \
        0,                                  /* tp_init */       \
        0,                                  /* tp_alloc */      \
        0                                   /* tp_new */        \
    };

/**
 * Implement static function <cls>_get_<propname> that queries COM object with function get_<propname>
 * converts the value into an python object and returns it.
 **/
#define LONG_PROPERTY_GETTER(cls, propname) \
    static PyObject* cls##_get_##propname(cls* self, void*) \
    { \
        long value; \
        HRESULT result = self->iface->get_##propname(&value); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return NULL; \
        } \
        return PyLong_FromLong(value); \
    }

/**
 * Implement static function <cls>_set_<propname>, that converty python object to long
 * and set it on the COM object with function put_<propname>.
 **/
#define LONG_PROPERTY_SETTER(cls, propname) \
    static int cls##_set_##propname(cls *self, PyObject* obj, void *) \
    { \
        PyObject* longObj = PyNumber_Long(obj); \
        if (!longObj) \
            return -1; \
        long value = PyLong_AsLong(longObj); \
        Py_DECREF(longObj); \
        HRESULT result = self->iface->put_##propname(value); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return -1; \
        } \
        return 0; \
    }

/**
 * Implement static function <cls>_get_<propname>, that queries COM object with function get_<propname>
 * converts the value into an python object and returns it.
 **/
#define DOUBLE_PROPERTY_GETTER(cls, propname) \
    static PyObject* cls##_get_##propname(cls* self, void*) \
    { \
        double value; \
        HRESULT result = self->iface->get_##propname(&value); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return NULL; \
        } \
        return PyFloat_FromDouble(value); \
    }

/**
 * Implement static function <cls>_set_<propname>, that converty python object to double
 * and set it on the COM object with function put_<propname>.
 **/
#define DOUBLE_PROPERTY_SETTER(cls, propname) \
    static int cls##_set_##propname(cls *self, PyObject* obj, void *) \
    { \
        PyObject* fltObj = PyNumber_Float(obj); \
        if (!fltObj) \
            return -1; \
        double value = PyFloat_AsDouble(fltObj); \
        Py_DECREF(fltObj); \
        HRESULT result = self->iface->put_##propname(value); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return -1; \
        } \
        return 0; \
    }

/**
 * Implement static function <cls>_get_<propname>, that queries COM object with function get_<propname>
 * converts the value into an python object and returns it.
 **/
#define BOOL_PROPERTY_GETTER(cls, propname) \
    static PyObject* cls##_get_##propname(cls* self, void*) \
    { \
        VARIANT_BOOL value; \
        HRESULT result = self->iface->get_##propname(&value); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return NULL; \
        } \
        if (value) \
            Py_RETURN_TRUE; \
        else \
            Py_RETURN_FALSE; \
    }

/**
 * Implement static function <cls>_set_<propname>, that converty python object to bool
 * and set it on the COM object with function put_<propname>.
 **/
#define BOOL_PROPERTY_SETTER(cls, propname) \
    static int cls##_set_##propname(cls *self, PyObject* obj, void *) \
    { \
        int test = PyObject_IsTrue(obj); \
        if (test < 0) \
            return -1; \
        VARIANT_BOOL value = test ? VARIANT_TRUE : VARIANT_FALSE; \
        HRESULT result = self->iface->put_##propname(value); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return -1; \
        } \
        return 0; \
    }

/**
 * Implement static function <cls>_get_<propname>, that queries COM object with function get_<propname>
 * converts the value into an long python object and returns it.
 **/
#define ENUM_PROPERTY_GETTER(cls, propname, enumtype) \
    static PyObject* cls##_get_##propname(cls* self, void*) \
    { \
        enumtype value; \
        HRESULT result = self->iface->get_##propname(&value); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return NULL; \
        } \
        return PyLong_FromLong((long)value); \
    }

/**
 * Implement static function <cls>_set_<propname>, that converty python object to long and then to the
 * enumtype and sets it on the COM object with function put_<propname>.
 **/
#define ENUM_PROPERTY_SETTER(cls, propname, enumtype) \
    static int cls##_set_##propname(cls *self, PyObject* obj, void *) \
    { \
        PyObject* longObj = PyNumber_Long(obj); \
        if (!longObj) \
            return -1; \
        long value = PyLong_AsLong(longObj); \
        Py_DECREF(longObj); \
        HRESULT result = self->iface->put_##propname((enumtype)value); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return -1; \
        } \
        return 0; \
    }

/**
 * Implement static function <cls>_get_<propname>, that queries Vector from COM object with function get_<propname>
 * and converts the value into an python tuple and returns it.
 **/
#define VECTOR_PROPERTY_GETTER(cls, propname) \
    static PyObject* cls##_get_##propname(cls *self, void *) \
    { \
        TEMScripting::Vector* vector; \
        HRESULT result = self->iface->get_##propname(&vector); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return NULL; \
        } \
        PyObject* tuple = tupleFromVector(vector); \
        vector->Release(); \
        return tuple; \
    }

/**
 * Implement static function <cls>_set_<propname>, that creates a Vector object
 * from the function get_<propname>, sets its value from a python tuple 
 * sets the vector on the COM object with function put_<propname>.
 **/
#define VECTOR_PROPERTY_SETTER(cls, propname) \
    static int cls##_set_##propname(cls *self, PyObject* obj, void *) \
    { \
        TEMScripting::Vector* vector; \
        HRESULT result = self->iface->get_##propname(&vector); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return -1; \
        } \
        if (!setVectorFromSequence(vector, obj)) { \
            vector->Release(); \
            return -1; \
        } \
        result = self->iface->put_##propname(vector); \
        vector->Release(); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return -1; \
        } \
        return 0; \
    }

/**
 * Implement static function <cls>_get_<propname>, that queries BSTR from COM object with function get_<propname>
 * converts the value into an python object and returns it.
 **/
#define STRING_PROPERTY_GETTER(cls, propname) \
    static PyObject* cls##_get_##propname(cls* self, void*) \
    { \
        BSTR value; \
        HRESULT result = self->iface->get_##propname(&value); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return NULL; \
        } \
        PyObject* strObj = PyUnicode_FromWideChar(value, SysStringLen(value)); \
        SysFreeString(value); \
        return strObj; \
    }

/**
 * Implement static function <cls>_get_<propname>, that queries SAFEARRAY from COM object with function get_<propname>
 * converts the value into an python object and returns it.
 **/
#define ARRAY_PROPERTY_GETTER(cls, propname) \
    static PyObject* cls##_get_##propname(cls* self, void*) \
    { \
        SAFEARRAY* arr = 0; \
        HRESULT result = self->iface->get_##propname(&arr); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return NULL; \
        } \
        PyObject* arrObj = arrayFromSafeArray(arr); \
        SafeArrayDestroy(arr); \
        return arrObj; \
    }

/**
 * Implement static function <cls>_get_<propname>, that queries <prop_iface> from COM object with function get_<propname>
 * and converts the value into the python type <prop_cls> and returns it.
 **/
#define OBJECT_PROPERTY_GETTER(cls, propname, prop_cls, prop_iface) \
    static PyObject* cls##_get_##propname(cls *self, void *) \
    { \
        prop_iface* iface; \
        HRESULT result = self->iface->get_##propname(&iface); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return NULL; \
        } \
        PyObject* obj = prop_cls##_create(iface); \
        if (!obj) \
            iface->Release(); \
        return obj; \
    }

/**
 * Implement static function <cls>_set_<propname>, that converts wrapper class <prop_cls>
 * to COM object <prop_iface> and sets it with the function put_<propname>.
 **/
#define OBJECT_PROPERTY_SETTER(cls, propname, prop_cls, prop_iface) \
    static int cls##_set_##propname(cls *self, PyObject* obj, void *) \
    { \
        prop_iface* iface = prop_cls##_query(obj); \
        if (!iface) { \
            PyErr_SetString(PyExc_TypeError, #prop_cls " expected."); \
            return -1; \
        } \
        HRESULT result = self->iface->put_##propname(iface); \
        if (FAILED(result)) { \
            raiseComError(result); \
            return -1; \
        } \
        return 0; \
    }

#endif // DEFINES_INC
