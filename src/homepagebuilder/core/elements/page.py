from abc import abstractmethod
from ..IO import File
from ..styles import get_style_code
from ..utils import PropertySetter
from ..utils.event import set_triggers
from ..formatter import format_code
from ..library import Library
from ..logger import Logger
from ..i18n import locale as t
from ..config import config
from ..types import BuildingEnvironment, PageBase

logger = Logger('Page')
class FileBasedPage(PageBase):
    "基于文件的页面，仅应用于继承"
    def __init__(self, file:File) -> None:
        super().__init__()
        self.file = file

class RawXamlPage(FileBasedPage):
    """纯XAML页面"""
    @property
    def display_name(self):
        return self.file.name

    def generate(self, env):
        return self.file.data

class CardStackPage(FileBasedPage):
    """卡片堆叠页面"""
    def __init__(self, file:File,) -> None:
        super().__init__(file)
        data = file.data
        self.setter = PropertySetter(data.get('fill'), data.get('override'))
        self.name = data.get('name', file.name)
        self.display_name_str = data.get('display_name', self.name)
        self.cardrefs = data.get('cards',{})
        self.alias = data.get('alias', [])
    
    @property
    def display_name(self):
        return self.display_name_str
    
    @set_triggers('page.generate')
    def generate(self, env):
        xaml = self.getframe(env)
        xaml = xaml.replace('${animations}', '')  # TODO
        xaml = xaml.replace('${content}', self.generate_content(env))
        xaml = xaml.replace('${styles}', get_style_code(env))
        return xaml

    def generate_content(self, env:BuildingEnvironment):
        """生成页面主要内容"""
        runtime_setter = self.setter.clone()
        runtime_setter.attach(env.get('setter'))
        content = ''
        for card_ref in self.cardrefs:
            content += self.__getcardscontent(card_ref, env, setter = runtime_setter)
        return content

    def __getcardscontent(self, ref:str, env:BuildingEnvironment, setter:PropertySetter):
        """一行可能有多个卡片，本方法处理整行"""
        ref = format_code(code=ref, data=setter.toProperties(), env=env)
        code = ''
        for each_card_ref in ref.split(';'):
            code += self.__getonecardcontent(each_card_ref, env, setter.clone())
        return code

    def __getonecardcontent(self, ref, env:BuildingEnvironment, setter:PropertySetter):
        """一行可能有多个卡片，本方法处理单个卡片"""
        ref = ref.replace(' ', '').split('|')
        real_ref = ref[0]
        args = ref[1:] if len(ref) > 1 else []
        if real_ref  == '':
            logger.info(t('project.get_card.null'))
            return ''
        setter.attach(PropertySetter.fromargs(args))
        logger.info(t('project.get_card', card_ref=real_ref))
        card = self.__getcard(real_ref,env,setter)
        if not card:
            return ''
        return env.get('builder').template_manager.build(card,env)
    
    def __getcard(self,ref,env:BuildingEnvironment,setter):
        if config('Debug.Enable'):
            return self.__getcardunsafe(ref, env, setter)
        try:
            return self.__getcardunsafe(ref, env, setter)
        except Exception as ex:
            logger.warning(t('project.get_card.failed', ex=ex))
            return None 
    
    def __getcardunsafe(self,ref,env:BuildingEnvironment,setter):
        card = env.get('project').base_library.get_card(ref, False)
        card = setter.decorate(card)
        return card
    
    def getframe(self,env:BuildingEnvironment):
        return env.get('project').resources.page_templates['Default']