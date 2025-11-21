#include <windows.h>
#include <strsafe.h>
#include <olectl.h>
#include <iostream>
#include "ITemscriptMockObject.h"

#define DEBUG_STREAM()    std::cout

// ============================================================
//  Debug helpers
// ============================================================
std::ostream& operator<<(std::ostream& os, const GUID& id) 
{
    char buffer[64];

    char* tmp = buffer;
    tmp += sprintf_s(buffer, 64, "%.8lX-%.4hX-%.4hX-", id.Data1, id.Data2, id.Data3);
    for (unsigned i = 0; i < sizeof(id.Data4); ++i) {
        tmp += sprintf_s(tmp, buffer + 64 - tmp, "%.2hhX", id.Data4[i]);
        if (i == 1)
            *tmp++ = '-';
    }

    os << buffer;
    return os;
}

// ============================================================
//  Global variables for server lifetime management
// ============================================================
LONG g_objCount = 0;
LONG g_serverLocks = 0;

// ============================================================
//  ChildMockObject implementing ITemscriptMockObject
// ============================================================
class ChildMockObject : public ITemscriptMockObject
{
public:
    ~ChildMockObject()
    {
        InterlockedDecrement(&g_objCount);
    }

    ChildMockObject() : refCount(1), value(999) 
    {
        InterlockedIncrement(&g_objCount);
    }

    // IUnknown
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** ppv) override
    {
        if (!ppv) return E_POINTER;

        if (IsEqualIID(riid, IID_IUnknown) || IsEqualIID(riid, IID_ITemscriptMockObject))
        {
            *ppv = static_cast<ITemscriptMockObject*>(this);
            AddRef();
            return S_OK;
        }

        *ppv = nullptr;
        return E_NOINTERFACE;
    }

    ULONG STDMETHODCALLTYPE AddRef() override
    {
        return InterlockedIncrement(&refCount);
    }

    ULONG STDMETHODCALLTYPE Release() override
    {
        ULONG r = InterlockedDecrement(&refCount);
        if (r == 0)
            delete this;
        return r;
    }

    // ISimpleCom
    HRESULT STDMETHODCALLTYPE get_Value(LONG* pVal) override
    {
        if (!pVal) return E_POINTER;
        *pVal = value;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE put_Value(LONG val) override
    {
        value = val;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE GetChild(ITemscriptMockObject** ppChild) override
    {
        // Children do not have sub-children (simplest case)
        *ppChild = nullptr;
        return S_OK;
    }

private:
    LONG refCount;
    LONG value;
};

// ============================================================
//  TemscriptMockObject implementing ISimpleCom
// ============================================================
class TemscriptMockObject : public ITemscriptMockObject
{
public:
    TemscriptMockObject() : refCount(1), value(0)
    {
        DEBUG_STREAM() << "TemscriptMockObject created @" << this << "\n";

        child = new ChildMockObject();
        InterlockedIncrement(&g_objCount);
    }

    ~TemscriptMockObject()
    {
        if (child)
            child->Release();
        InterlockedDecrement(&g_objCount);
    }

    // IUnknown
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** ppv) override
    {
        if (!ppv) return E_POINTER;

        if (IsEqualIID(riid, IID_IUnknown) || IsEqualIID(riid, IID_ITemscriptMockObject))
        {
            *ppv = static_cast<ITemscriptMockObject*>(this);
            AddRef();
            return S_OK;
        }

        *ppv = nullptr;
        return E_NOINTERFACE;
    }

    ULONG STDMETHODCALLTYPE AddRef() override
    {
        ULONG r = InterlockedIncrement(&refCount);
        DEBUG_STREAM() << "TemscriptMockObject(" << this << ")::AddRef -> " << r << "\n";
        return r;
    }

    ULONG STDMETHODCALLTYPE Release() override
    {
        ULONG r = InterlockedDecrement(&refCount);
        DEBUG_STREAM() << "TemscriptMockObject(" << this << ")::Release -> " << r << "\n";
        if (r == 0)
            delete this;
        return r;
    }

    // ISimpleCom
    HRESULT STDMETHODCALLTYPE get_Value(LONG* pVal) override
    {
        if (!pVal) 
            return E_POINTER;

        DEBUG_STREAM() << "TemscriptMockObject(" << this << ")::get_Value -> " << value << "\n";

        *pVal = value;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE put_Value(LONG val) override
    {
        DEBUG_STREAM() << "TemscriptMockObject(" << this << ")::put_Value -> " << val << "\n";

        value = val;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE GetChild(ITemscriptMockObject** ppChild) override
    {
        if (!ppChild) return E_POINTER;
        child->AddRef();      // Give the caller a reference
        *ppChild = child;
        return S_OK;
    }

private:
    LONG refCount;
    LONG value;
    ITemscriptMockObject* child;
};

// ============================================================
//  Class factory
// ============================================================
class MockObjectFactory : public IClassFactory
{
public:
    ~MockObjectFactory()
    {
        InterlockedDecrement(&g_objCount);
    }

    MockObjectFactory() : refCount(1) 
    {
        InterlockedIncrement(&g_objCount);
    }

    // IUnknown
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** ppv) override
    {
        if (!ppv)
            return E_POINTER;

        DEBUG_STREAM() << "MockObjectFactory::QueryInterface " << riid << "\n";

        if (IsEqualIID(riid, IID_IUnknown) || IsEqualIID(riid, IID_IClassFactory))
        {
            *ppv = static_cast<IClassFactory*>(this);
            AddRef();
            return S_OK;
        }

        *ppv = nullptr;
        return E_NOINTERFACE;
    }

    ULONG STDMETHODCALLTYPE AddRef() override
    {
        return InterlockedIncrement(&refCount);
    }

    ULONG STDMETHODCALLTYPE Release() override
    {
        ULONG r = InterlockedDecrement(&refCount);
        if (r == 0)
            delete this;
        return r;
    }

    // IClassFactory
    HRESULT STDMETHODCALLTYPE CreateInstance(IUnknown* outer, REFIID riid, void** ppv) override
    {
        if (!ppv) 
            return E_POINTER;    
        *ppv = nullptr;

        if (outer != nullptr)
            return CLASS_E_NOAGGREGATION;

        //std::cout << "MockObjectFactory::CreateInstance " << riid << "\n";

        TemscriptMockObject* obj = new TemscriptMockObject();
        *ppv = obj;
        return S_OK;
        HRESULT hr = obj->QueryInterface(riid, ppv);
        obj->Release();

        return hr;
    }

    HRESULT STDMETHODCALLTYPE LockServer(BOOL lock) override
    {
        if (lock)
            InterlockedIncrement(&g_serverLocks);
        else
            InterlockedDecrement(&g_serverLocks);

        return S_OK;
    }

private:
    LONG refCount;
};

// ============================================================
//  Standard COM DLL functions
// ============================================================

static HINSTANCE g_hInstance;

BOOL APIENTRY DllMain(HMODULE hinstDLL, DWORD reason, LPVOID)
{
    if (reason == DLL_PROCESS_ATTACH) {
        g_hInstance = hinstDLL;
        DisableThreadLibraryCalls(hinstDLL);
    }

    return TRUE;
}

extern "C" HRESULT __stdcall DllCanUnloadNow(void)
{
    // The DLL can be unloaded only if there are no outstanding objects and no server locks.
    if (g_objCount == 0 && g_serverLocks == 0)
    {
        return S_OK; // OK to unload
    }
    else
    {
        return S_FALSE; // Not OK to unload
    }
}

extern "C" HRESULT __stdcall DllGetClassObject(REFCLSID clsid, REFIID iid, void** ppv)
{
    DEBUG_STREAM() << "DllGetClassObject clsid=" << clsid << ", iid=" << iid << "\n";

    if (!IsEqualCLSID(clsid, CLSID_TemscriptMockObject))
        return CLASS_E_CLASSNOTAVAILABLE;

    MockObjectFactory* factory = new MockObjectFactory();
    HRESULT hr = factory->QueryInterface(iid, ppv);
    factory->Release();

    return hr;
}

extern "C" HRESULT __stdcall DllRegisterServer(void)
{
    HKEY hKey;
    WCHAR path[MAX_PATH];

    // Get DLL path
    GetModuleFileNameW(g_hInstance, path, MAX_PATH);

    // CLSID key
    WCHAR clsidStr[64];
    StringFromGUID2(CLSID_TemscriptMockObject, clsidStr, 64);

    WCHAR keyPath[128];
    wsprintfW(keyPath, L"CLSID\\%s\\InprocServer32", clsidStr);

    // Create registry keys
    if (RegCreateKeyW(HKEY_CLASSES_ROOT, keyPath, &hKey) != ERROR_SUCCESS)
        return SELFREG_E_CLASS;

    RegSetValueExW(hKey, nullptr, 0, REG_SZ, (BYTE*)path,
                   (DWORD)((wcslen(path) + 1) * sizeof(WCHAR)));

    RegSetValueExW(hKey, L"ThreadingModel", 0,
                   REG_SZ, (BYTE*)L"Both", 10 * sizeof(WCHAR));

    RegCloseKey(hKey);
    return S_OK;
}

extern "C" HRESULT __stdcall DllUnregisterServer(void)
{
    WCHAR clsidStr[64];
    StringFromGUID2(CLSID_TemscriptMockObject, clsidStr, 64);

    WCHAR keyPath[128];
    wsprintfW(keyPath, L"CLSID\\%s", clsidStr);

    RegDeleteTreeW(HKEY_CLASSES_ROOT, keyPath);
    return S_OK;
}

