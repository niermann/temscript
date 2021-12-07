import numpy as np

from temscript.remote_microscope import ExtendedJsonEncoder
from temscript.enums import *

print("RequestJsonEncoder:")
reqenc = ExtendedJsonEncoder()

print("\tint:", reqenc.encode(123))
print("\tnp.int64:", reqenc.encode(np.int64(123)))
print("\tnp.float32:", reqenc.encode(np.float32(123.45)))
print("\ttuple:", reqenc.encode((1, 2, 3)))
print("\tlist:", reqenc.encode([1, 2, 3]))
print("\tgenerator:", reqenc.encode(range(3)))
print("\tnp.array:", reqenc.encode(np.arange(3)))
print("\tStageStatus.MOVING:", reqenc.encode(StageStatus.MOVING))

