#include "temscript.h"
#include "defines.h"
#include "types.h"

ENUM_PROPERTY_GETTER(Stage, Status, TEMScripting::StageStatus)
ENUM_PROPERTY_GETTER(Stage, Holder, TEMScripting::StageHolderType)

static PyObject* buildPositionDict(TEMScripting::StagePosition* position)
{
    PyObject* dict = PyDict_New();
    double value;

    HRESULT result = position->get_X(&value);
    if (FAILED(result))
        goto error;
    PyObject* obj = PyFloat_FromDouble(value);
    PyDict_SetItemString(dict, "x", obj);
    Py_XDECREF(obj);

    result = position->get_Y(&value);
    if (FAILED(result))
        goto error;
    obj = PyFloat_FromDouble(value);
    PyDict_SetItemString(dict, "y", obj);
    Py_XDECREF(obj);

    result = position->get_Z(&value);
    if (FAILED(result))
        goto error;
    obj = PyFloat_FromDouble(value);
    PyDict_SetItemString(dict, "z", obj);
    Py_XDECREF(obj);

    result = position->get_A(&value);
    if (FAILED(result))
        goto error;
    obj = PyFloat_FromDouble(value);
    PyDict_SetItemString(dict, "a", obj);
    Py_XDECREF(obj);

    result = position->get_B(&value);
    if (FAILED(result))
        goto error;
    obj = PyFloat_FromDouble(value);
    PyDict_SetItemString(dict, "b", obj);
    Py_XDECREF(obj);

    return dict;

error:
    Py_XDECREF(dict);
    raiseComError(result);
    return NULL;
}

static PyObject* Stage_get_Position(Stage *self, void *)
{
    TEMScripting::StagePosition* position;
    
    HRESULT result = self->iface->get_Position(&position);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    PyObject* dict = buildPositionDict(position);
    position->Release();
    return dict;
}

/**
 * Return: 1 if value is returned
 *         0 if value is NULL or None
 *        -1 on error
 */
static int getFloat(PyObject* obj, double& value)
{
    if (!obj || obj == Py_None)
        return 0;
    PyObject* fltObj = PyNumber_Float(obj);
    if (!fltObj)
        return -1;
    value = PyFloat_AsDouble(fltObj);
    Py_DECREF(fltObj);
    return 1;
}

/**
 * Parse stage position dictionary into StagePosition instance.
 * On return a bitmap with set axes is returned in *axes*.
 * If *speed* is non-NULL and a float-value for "speed" is set in *kw*, *speed* is uptdated to the new value.
 * Return: true, on success
 */
static bool parsePosition(PyObject* args, PyObject* kw, TEMScripting::StagePosition* position, unsigned& axes, double* speed=NULL)
{
    PyObject* xObj = NULL;
    PyObject* yObj = NULL;
    PyObject* zObj = NULL;
    PyObject* aObj = NULL;
    PyObject* bObj = NULL;
	PyObject* speedObj = NULL;
    
    static const char* kwlist[] = { "x", "y", "z", "a", "b", "speed", NULL };

    double  value;
    int     test;
    
    if (!PyArg_ParseTupleAndKeywords(args, kw, "|OOOOOO", (char**)kwlist, &xObj, &yObj, &zObj, &aObj, &bObj, &speedObj))
        return false;
        
    axes = 0;
    
    test = getFloat(xObj, value);
    if (test > 0) {
        HRESULT result = position->put_X(value);
        if (FAILED(result)) {
            raiseComError(result);
            return false;
        }
        axes |= TEMScripting::axisX;
    } else if (test < 0)
        return false;
    
    test = getFloat(yObj, value);
    if (test > 0) {
        HRESULT result = position->put_Y(value);
        if (FAILED(result)) {
            raiseComError(result);
            return false;
        }
        axes |= TEMScripting::axisY;
    } else if (test < 0)
        return false;
        
    test = getFloat(zObj, value);
    if (test > 0) {
        HRESULT result = position->put_Z(value);
        if (FAILED(result)) {
            raiseComError(result);
            return false;
        }
        axes |= TEMScripting::axisZ;
    } else if (test < 0)
        return false;
        
    test = getFloat(aObj, value);
    if (test > 0) {
        HRESULT result = position->put_A(value);
        if (FAILED(result)) {
            raiseComError(result);
            return false;
        }
        axes |= TEMScripting::axisA;
    } else if (test < 0)
        return false;
        
    test = getFloat(bObj, value);
    if (test > 0) {
        HRESULT result = position->put_B(value);
        if (FAILED(result)) {
            raiseComError(result);
            return false;
        }
        axes |= TEMScripting::axisB;
    } else if (test < 0)
        return false;

	if (speed) {
		test = getFloat(speedObj, value);
		if (test > 0)
			*speed = value;
		else if (test < 0)
			return false;
	}

    return true;
}

static PyObject* Stage_GoTo(Stage *self, PyObject* args, PyObject* kw)
{
    unsigned axes = 0;
	double speed = 1.0;
    
    TEMScripting::StagePosition* position;
    HRESULT result = self->iface->get_Position(&position);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }
    
    if (!parsePosition(args, kw, position, axes, &speed)) {
        position->Release();
        return NULL;
    }

    if (axes) {
		if (speed != 1.0)
			result = self->iface->raw_GotoWithSpeed(position, (TEMScripting::StageAxes)axes, speed);
		else
			result = self->iface->raw_Goto(position, (TEMScripting::StageAxes)axes);
        if (FAILED(result)) {
		    position->Release();
            raiseComError(result);
            return NULL;
        }
    }

    position->Release();
    Py_RETURN_NONE;
}

static PyObject* Stage_MoveTo(Stage *self, PyObject* args, PyObject* kw)
{
    unsigned axes = 0;
   
    TEMScripting::StagePosition* position;
    HRESULT result = self->iface->get_Position(&position);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    if (!parsePosition(args, kw, position, axes)) {
        position->Release();
        return NULL;
    }

    if (axes) {
        result = self->iface->raw_MoveTo(position, (TEMScripting::StageAxes)axes);
        if (FAILED(result)) {
			position->Release();
            raiseComError(result);
            return NULL;
        }
    }

    position->Release();
    Py_RETURN_NONE;
}

static PyObject* Stage_AxisData(Stage *self, PyObject* args)
{
    const char* axisStr;

    if (!PyArg_ParseTuple(args, "s", &axisStr)) 
        return NULL;

    TEMScripting::StageAxes axis;
    if (strcmp(axisStr, "x") == 0)
        axis = TEMScripting::axisX;
    else if (strcmp(axisStr, "y") == 0)
        axis = TEMScripting::axisY;
    else if (strcmp(axisStr, "z") == 0)
        axis = TEMScripting::axisZ;
    else if (strcmp(axisStr, "a") == 0)
        axis = TEMScripting::axisA;
    else if (strcmp(axisStr, "b") == 0)
        axis = TEMScripting::axisB;
    else {
        PyErr_SetString(PyExc_ValueError, "Use value 'x', 'y', 'z', 'a', and 'b' to specify axis.");
        return NULL;
    }

    TEMScripting::StageAxisData* data;
    HRESULT result = self->iface->get_AxisData(axis, &data);
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    double minPos;
    result = data->get_MinPos(&minPos);
    if (FAILED(result)) {
        data->Release();
        raiseComError(result);
        return NULL;
    }

    double maxPos;
    result = data->get_MaxPos(&maxPos);
    if (FAILED(result)) {
        data->Release();
        raiseComError(result);
        return NULL;
    }

    TEMScripting::MeasurementUnitType type;
    result = data->get_UnitType(&type);
    data->Release();
    if (FAILED(result)) {
        raiseComError(result);
        return NULL;
    }

    const Py_UNICODE* typeStr;
    switch (type) {
    case TEMScripting::MeasurementUnitType_Meters:
        typeStr = L"meters"; break;
    case TEMScripting::MeasurementUnitType_Radians:
        typeStr = L"radians"; break;
    default:
        typeStr = NULL; break;
    }

    return Py_BuildValue("ddu", minPos, maxPos, typeStr);
}

static PyGetSetDef Stage_getset[] = {
    {"Status",      (getter)&Stage_get_Status, NULL, NULL, NULL},
    {"Holder",      (getter)&Stage_get_Holder, NULL, NULL, NULL},
    {"Position",    (getter)&Stage_get_Position, NULL, NULL, NULL},
    {NULL}  /* Sentinel */
};

static PyMethodDef Stage_methods[] = {
    {"GoTo",     (PyCFunction)&Stage_GoTo, METH_VARARGS|METH_KEYWORDS, NULL},
    {"MoveTo",   (PyCFunction)&Stage_MoveTo, METH_VARARGS|METH_KEYWORDS, NULL},
    {"AxisData", (PyCFunction)&Stage_AxisData, METH_VARARGS, NULL},
    {NULL}  /* Sentinel */
};

IMPLEMENT_WRAPPER(Stage, TEMScripting::Stage, Stage_getset, Stage_methods)
