#include <windows.h>
#include <strsafe.h>
#include "ISimpleCom.h"
#include "SimpleComClassID.h"

// ============================================================
//  ChildComObject implementing ISimpleCom
// ============================================================
class ChildComObject : public ISimpleCom
{
public:
    ChildComObject() : refCount(1), value(999) {}

    // IUnknown
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** ppv) override
    {
        if (!ppv) return E_POINTER;

        if (riid == IID_IUnknown || riid == IID_ISimpleCom)
        {
            *ppv = static_cast<ISimpleCom*>(this);
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

    HRESULT STDMETHODCALLTYPE GetChild(ISimpleCom** ppChild) override
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
//  SimpleComObject implementing ISimpleCom
// ============================================================
class SimpleComObject : public ISimpleCom
{
public:
    SimpleComObject() : refCount(1), value(0)
    {
        child = new ChildComObject();
    }

    ~SimpleComObject()
    {
        if (child)
            child->Release();
    }

    // IUnknown
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** ppv) override
    {
        if (!ppv) return E_POINTER;

        if (riid == IID_IUnknown || riid == IID_ISimpleCom)
        {
            *ppv = static_cast<ISimpleCom*>(this);
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

    HRESULT STDMETHODCALLTYPE GetChild(ISimpleCom** ppChild) override
    {
        if (!ppChild) return E_POINTER;
        child->AddRef();      // Give the caller a reference
        *ppChild = child;
        return S_OK;
    }

private:
    LONG refCount;
    LONG value;
    ISimpleCom* child;
};

// ============================================================
//  Class factory
// ============================================================
class SimpleComFactory : public IClassFactory
{
public:
    SimpleComFactory() : refCount(1) {}

    // IUnknown
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** ppv) override
    {
        if (!ppv) return E_POINTER;

        if (riid == IID_IUnknown || riid == IID_IClassFactory)
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
        if (outer != nullptr)
            return CLASS_E_NOAGGREGATION;

        SimpleComObject* obj = new SimpleComObject();
        return obj->QueryInterface(riid, ppv);
    }

    HRESULT STDMETHODCALLTYPE LockServer(BOOL lock) override
    {
        if (lock)
            InterlockedIncrement(&serverLocks);
        else
            InterlockedDecrement(&serverLocks);

        return S_OK;
    }

private:
    LONG refCount;
    static inline LONG serverLocks = 0;
};

// Global DLL reference count
static LONG g_dllRefCount = 0;

// ============================================================
//  Standard COM DLL functions
// ============================================================

BOOL APIENTRY DllMain(HMODULE, DWORD, LPVOID)
{
    return TRUE;
}

extern "C" HRESULT __stdcall DllCanUnloadNow(void)
{
    if (g_dllRefCount == 0)
        return S_OK;
    return S_FALSE;
}

extern "C" HRESULT __stdcall DllGetClassObject(REFCLSID clsid, REFIID iid, void** ppv)
{
    if (clsid != CLSID_SimpleComObject)
        return CLASS_E_CLASSNOTAVAILABLE;

    SimpleComFactory* factory = new SimpleComFactory();
    return factory->QueryInterface(iid, ppv);
}

extern "C" HRESULT __stdcall DllRegisterServer(void)
{
    HKEY hKey;
    WCHAR path[MAX_PATH];

    // Get DLL path
    GetModuleFileNameW((HMODULE)&__ImageBase, path, MAX_PATH);

    // CLSID key
    WCHAR clsidStr[64];
    StringFromGUID2(CLSID_SimpleComObject, clsidStr, 64);

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
    StringFromGUID2(CLSID_SimpleComObject, clsidStr, 64);

    WCHAR keyPath[128];
    wsprintfW(keyPath, L"CLSID\\%s", clsidStr);

    RegDeleteTreeW(HKEY_CLASSES_ROOT, keyPath);
    return S_OK;
}

