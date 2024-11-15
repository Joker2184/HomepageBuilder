"""构建器主入口"""
import argparse
import os
from os import makedirs
from os.path import sep, exists
from .core.config import init_full, force_debug
from .debug import global_anlyzer as anl

def build_and_output(project, page, output_path):
    xaml = project.get_page_xaml(page_alias=page)
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xaml)


def command_build(args):
    from .core.builder import Builder
    builder = Builder()
    builder.load_proejct(args.project)
    output_path = args.output_path
    anl.phase('构建页面')
    anl.switch_in()
    if args.all_page:
        if not exists(args.output_path):
            makedirs(args.output_path, exist_ok=True)
        for page in builder.current_project.get_all_pagename():
            if not args.output_path.endswith(sep):
                output_path = output_path + sep
            if args.dry_run:
                page_output_path = None
            else:
                page_output_path = f"{output_path}{page}.xaml"
            build_and_output(builder.current_project, page, page_output_path)
    else:
        page = args.page
        if not page:
            page = builder.current_project.default_page
        if args.dry_run:
            page_output_path = None
        else:
            page_output_path = f"{output_path}"
        build_and_output(builder.current_project, page, page_output_path)
    anl.stop()
    anl.summarize()

def command_server(args):
    from .server.main import Server
    server = Server(args.project)
    server.run(args.port if args.port else 6608)


command_func_mapping = {
    'build': command_build,
    'server': command_server
}

def main():
    """构建器主入口"""
    anl.phase('初始化构建器配置')
    init_full()
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='start debug mode')
    subparsers = parser.add_subparsers(help='Command', dest='command')
    parser_build = subparsers.add_parser('build', help='Build homepage')
    parser_server = subparsers.add_parser('server', help='Start server')
    parser_build.add_argument('--project', type=str,
                              default=os.getcwd() + os.path.sep + 'Project.yml',
                              help='project file path')
    parser_build.add_argument('--output-path', type=str,
                              default= os.getcwd() + os.path.sep + 'output.xaml',
                              help='generated file dest')
    parser_build.add_argument('-p', '--page', type=str, help='page name')
    parser_build.add_argument('-a', '--all-page', action='store_true', help='generate all page')
    parser_build.add_argument('--dry-run', action='store_true', help='dry run')
    parser_server.add_argument('--project', type=str,
                              default=os.getcwd() + os.path.sep + 'Project.yml',
                              help='project file path')
    parser_server.add_argument('-p', '--port', type=str, help='project path')
    args = parser.parse_args()
    if args.debug:
        force_debug()
    command_func_mapping[args.command](args)


if __name__ == '__main__':
    main()
