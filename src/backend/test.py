from typing import Dict
from litestar import Controller, get

# # from actorsAlgorithm import castingAlgorithm as cast


class Test(Controller):
    path = "/test"

    @get()
    async def test_get(self) -> Dict[str,str]:
        return {"hello": "word !!"}