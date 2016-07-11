#ifndef TEMSCRIPT_INC
#define TEMSCRIPT_INC

// General remark, about COM heap objects, i.e. BSTR and SAFEARRAY:
// The ownership of these things are passed to you if they are an [out] parameter, i.e. in method 
// arguments of type BSTR*. You are the owner (and don't loose your ownership) if its an [in] parameter, 
// i.e. arguments of type BSTR.

#define PY_ARRAY_UNIQUE_SYMBOL  _temscript_numpy_API
#define NPY_NO_DEPRECATED_API   NPY_1_7_API_VERSION

#include <Python.h>

// Use this statement to use the type library from your own stdscript.dll
//#import "stdscript.dll" named_guids raw_interfaces_only raw_method_prefix("raw_")

// Use header created from typelib
#include "stdscript.tlh"

// Use this statement, if the namespace of your TEM scripting interface is still called "Tecnai"
//namespace TEMScripting = Tecnai;

// Enable debug output
//#define DEBUGF(...) printf(__VA_ARGS__)
#define DEBUGF(...) do {} while(0)
    
// Set temscript version string
#define TEMSCRIPT_VERSION "1.0.5"

#define COMPILE_TIME_ASSERT(expr)   extern int __some_arbitrary_symbol[(int)(expr)];

// On win platforms this is usually true... needed to get string encoding right
COMPILE_TIME_ASSERT(sizeof(OLECHAR) == sizeof(Py_UNICODE))

// Needed for variant handling
COMPILE_TIME_ASSERT(sizeof(long) == 4);

// Global objects
extern PyObject* comError;
extern PyObject* temscriptModule;

// Helpers (in module.cpp)
void      raiseComError(HRESULT result);
PyObject* arrayFromSafeArray(SAFEARRAY* arr);
PyObject* tupleFromVector(TEMScripting::Vector* vec);
bool      setVectorFromSequence(TEMScripting::Vector* vec, PyObject* seq);

#endif // TEMSCRIPT_INC
