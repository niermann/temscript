#pragma once
#include <windows.h>

// {2F4A04D8-76E2-4F6B-AE18-8C4A55E675DD}
static const GUID IID_ISimpleCom =
{ 0x2f4a04d8, 0x76e2, 0x4f6b, {0xae, 0x18, 0x8c, 0x4a, 0x55, 0xe6, 0x75, 0xdd} };

interface ISimpleCom : public IUnknown
{
    virtual HRESULT STDMETHODCALLTYPE get_Value(LONG* pVal) = 0;
    virtual HRESULT STDMETHODCALLTYPE put_Value(LONG val) = 0;

    // NEW: Returns another internal COM object that also implements ISimpleCom
    virtual HRESULT STDMETHODCALLTYPE GetChild(ISimpleCom** ppChild) = 0;
};

