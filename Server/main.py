'''
服务器主模块
'''
import traceback
from flask import Flask, request
from Core.project import PageNotFoundError
from Core.debug import Logger
from Server.project_updater import request_update
from Server.project_api import ProjectAPI
from Core.i18n import locale as t

logger = Logger('Server')
app = Flask(__name__)
projapi = None

class Server:

    def __init__(self,project_path=None):
        global projapi
        logger.info(t('server.init'))
        projapi = ProjectAPI(project_path)

    def run(self,port):
        logger.info(t('server.start',port=port))
        app.run(port=port)

    def get_flask_app(self):
        return app

@app.route("/pull",methods=['POST'])
def git_update():
    '''收到 github 更新信号更新工程文件'''
    status,data = request_update(request,projapi.project_dir,
        projapi.config['github_secret'])
    if status == 200:
        projapi.clear_cache()
    else:
        logger.error(data)
    return data,status

@app.route("/")
def index_page():
    '''默认界面'''
    if projapi.default_page:
        return getpage(projapi.default_page)
    else:
        return 'No Page Found',404

@app.route("/<path:alias>")
def getpage(alias:str):
    '''默认页面'''
    if alias.endswith('/version') or alias == 'version':
        return projapi.get_version()
    while alias.endswith('/'):
        alias = alias[:-1]
    try:
        if alias.endswith('.json'):
            return projapi.get_page_json(alias[:-5])
        if alias.endswith('.xaml'):
            alias = alias[:-5]
        return projapi.get_page_xaml(alias)
    except PageNotFoundError:
        if alias == 'could_you_buy_me_a_coffee':
            return 'Sure You Need A Coffee And I AM A TEAPOT',418
        return 'No Page Found',404
    except Exception:
        logger.error(traceback.format_exc())
        return 'Inner Error Occured',500

if __name__ == "__main__":
    s = Server()
    s.run(6608)