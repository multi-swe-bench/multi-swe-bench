"""
This script is used to check the syntax error brought by merge the pr created by envagent.
"""

import os
data_path=''
common_dir= '/home/aoyanli.722/MSB_for_envagent_test/multi_swe_bench/harness/repos'
languages=['python', 'cpp', 'php', 'kotlin', 'csharp', 'scala', 'swift', 'typescript', 'ruby', 'html', 'golang', 'javascript', 'rust', 'c', 'java']

def remove_unkonwn_file():
    remove_file_names=[]
    for lang in languages:
        for root,dirs,files in os.walk(os.path.join(common_dir, lang)):
            for file in files:
                if file.endswith('.py') and '_to_unknown' in file:
                    remove_file_names.append(os.path.join(root, file))
    
    for file in remove_file_names:
        print(file)
        # os.remove(file)

def process_init_file():
    init_content=""
    for lang in languages:
        with open(f'{common_dir}/{lang}/__init__.py', 'r') as f:
            init_content += f.read()

    # ensure the newly added repo in init_content
    for file in os.listdir(data_path):
        org = file.split('__')[0]
        if org.startswith('.'):
            continue
        if org.replace('-','_').replace('.','_') not in init_content:
            print(f'{org} not in init_content')
    
    # del the incomplete(rebundant) repo
    # 在提交pr的时候，同一个机器的其他repo没有配置完，unknow删掉，init也得删掉
    for lang in languages:
        done_org= os.listdir(os.path.join(common_dir, lang))
        remain_importlines=""
        with open(os.path.join(common_dir, lang,'__init__.py'), 'r') as f:
            importlines= [i.strip() for i in f.readlines()]
        for line in importlines:
            orgname = line.split(' import *')[0].split('.')[-1]
            if orgname not in done_org:
                print(f'{orgname} not in done_org')
            else:
                remain_importlines += line+'\n'
        # replace the repo in lang init file
        # with open(os.path.join(common_dir, lang,'__init__replace.py'), 'w') as f:
        #     f.write(remain_importlines) 

    # del unkonw对应的repo目录下init
    for lang in languages:
        for root,dirs,files in os.walk(os.path.join(common_dir, lang)):
            for file in files:
                if file == '__init__.py':
                    with open(os.path.join(root, file), 'r') as f:
                        init_repos= [i.strip() for i in f.readlines()]
                    del_init_repos=[]
                    for init_repo in init_repos:
                        if '_to_unknown' in init_repo:
                            print(f'need del some repo in {root}/{file}')
                        else:
                            del_init_repos.append(init_repo)
                    # with open(os.path.join(root, file), 'w') as f:
                    #     f.write('\n'.join(del_init_repos))        
                    
if __name__== '__main__':
    process_init_file()
    # remove_unkonwn_file()