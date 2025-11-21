from temscript._com import CLSCTX_ALL, IUnknown, co_create_instance
from temscript._instrument_com import LongProperty, ObjectProperty
from uuid import UUID

CLSID_MockObject = UUID('e5766dfa-303e-48a9-983e-352fa4a5a408')

class IChildObject(IUnknown):
    IID = UUID('bbbd2968-4b93-49a9-b1ae-16d1d6b563eb')

    value = LongProperty(get_index=4, put_index=5)


class IMockObject(IUnknown):
    IID = UUID('bbbd2968-4b93-49a9-b1ae-16d1d6b563eb')

    value = LongProperty(get_index=4, put_index=5)
    child = ObjectProperty(IChildObject, get_index=6)


def test_mock_object():
    obj = co_create_instance(CLSID_MockObject, CLSCTX_ALL, IMockObject)
    print(obj.value)
    obj.value = 123
    assert obj.value == 123

    child = obj.child
    child.value = 321
    assert child.value == 123
    assert obj.value == 123


test_mock_object()
