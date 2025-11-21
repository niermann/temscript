#pragma once
#include <windows.h>

// {e5766dfa-303e-48a9-983e-352fa4a5a408}
const CLSID CLSID_TemscriptMockObject = { 0xe5766dfa, 0x303e, 0x48a9, {0x98, 0x3e, 0x35, 0x2f, 0xa4, 0xa5, 0xa4, 0x08} };

// {bbbd2968-4b93-49a9-b1ae-16d1d6b563eb}
static const GUID IID_ITemscriptMockObject = { 0xbbbd2968, 0x4b93, 0x49a9, {0xb1, 0xae, 0x16, 0xd1, 0xd6, 0xb5, 0x63, 0xeb} };

interface ITemscriptMockObject : public IUnknown
{
    virtual HRESULT STDMETHODCALLTYPE get_Value(LONG* pVal) = 0;
    virtual HRESULT STDMETHODCALLTYPE put_Value(LONG val) = 0;

    // NEW: Returns another internal COM object that also implements ISimpleCom
    virtual HRESULT STDMETHODCALLTYPE GetChild(ITemscriptMockObject** ppChild) = 0;
};

