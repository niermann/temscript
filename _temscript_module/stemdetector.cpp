#include "temscript.h"
#include "defines.h"
#include "types.h"

struct STEMDetector {
    PyObject_HEAD
    PyObject*                   weakRefList;
    TEMScripting::STEMDetector* iface;
    PyObject*                   acqParams;
};

OBJECT_PROPERTY_GETTER(STEMDetector, Info, STEMDetectorInfo, TEMScripting::STEMDetectorInfo)

static PyObject* STEMDetector_get_AcqParams(STEMDetector *self, void *)
{
    PyObject* obj = self->acqParams;
    Py_XINCREF(obj);
    return obj;
}

static PyGetSetDef STEMDetector_getset[] = {
    {"Info",        (getter)&STEMDetector_get_Info, NULL, NULL, NULL},
    {"AcqParams",   (getter)&STEMDetector_get_AcqParams, NULL, NULL, NULL},
    {NULL}  /* Sentinel */
};

static void STEMDetector_dealloc(STEMDetector* self)
{ 
    DEBUGF("STEMDetector(%p): dealloc\n", self);
    if (self->weakRefList != NULL)
        PyObject_ClearWeakRefs((PyObject*)self);
    Py_CLEAR(self->acqParams);
    self->iface->Release();
    self->iface = NULL;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyObject* STEMDetector_create(TEMScripting::STEMDetector* iface, PyObject* acqParams)
{
    STEMDetector* self = PyObject_NEW(STEMDetector, &STEMDetector_Type);
    if (self) {
        Py_XINCREF(acqParams);
        self->acqParams   = acqParams;
        self->iface       = iface;
        self->weakRefList = NULL;
        DEBUGF("STEMDetector(%p): create(%p)\n", self, iface);
    }
    return (PyObject *)self;
}

TEMScripting::STEMDetector* STEMDetector_query(PyObject* self)
{
    if (!self || !PyObject_TypeCheck(self, &STEMDetector_Type))
        return NULL;
    return reinterpret_cast<STEMDetector*>(self)->iface;
}

PyTypeObject STEMDetector_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "temscript.STEMDetector",           /*tp_name*/
    sizeof(STEMDetector),              /*tp_basicsize*/  
    0,                                  /*tp_itemsize*/
    (destructor)STEMDetector_dealloc,   /*tp_dealloc*/
    0,                                  /*tp_print*/
    0,                                  /*tp_getattr*/
    0,                                  /*tp_setattr*/
    0,                                  /*tp_compare*/
    0,                                  /*tp_repr*/
    0,                                  /*tp_as_number*/
    0,                                  /*tp_as_sequence*/
    0,                                  /*tp_as_mapping*/
    0,                                  /*tp_hash */
    0,                                  /*tp_call*/
    0,                                  /*tp_str*/
    0,                                  /*tp_getattro*/
    0,                                  /*tp_setattro*/
    0,                                  /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    0,                                  /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    offsetof(STEMDetector, weakRefList),/* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    0,                                  /* tp_methods */
    0,                                  /* tp_members */
    STEMDetector_getset,                /* tp_getset */ 
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    0,                                  /* tp_init */
    0,                                  /* tp_alloc */
    0                                   /* tp_new */
};

