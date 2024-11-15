from typing import List, TYPE_CHECKING
from ..utils.finder import find_using_resources
from ..formatter import format_code

if TYPE_CHECKING:
    from core.io import File
    from core.types import BuildingEnvironment

class Component:
    def __init__(self, file: 'File') -> None:
        self.file:File = file
        self.used_resources:List[str] = self.__findusedresources()

    def toxaml(self, card, env, children_code = '') -> str:
        self.mark_used_resources(card,env)
        return format_code(code = self.file.data,data = card,env=env,children_code=children_code)

    def __findusedresources(self):
        return find_using_resources(self.file)

    def mark_used_resources(self,card,env:'BuildingEnvironment'):
        for res_ref in self.used_resources:
            res_ref = format_code(code = res_ref,data=card,env=env)
            env.get('used_resources').add(res_ref)

    def __str__(self) -> str:
        return self.file.data