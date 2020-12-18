'''
Author: your name
Date: 2020-12-14 14:47:51
LastEditTime: 2020-12-14 15:35:46
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \leetcodei:\python-workspace\awsome-python-web\www\read_config.py
读取配置文件
'''
import os
import yaml
import logging



def read_config(yamlPath=None):
    """
    读取yaml配置文件
    """
    if yamlPath is None:
        # 获取当前脚本所在文件夹路径
        curPath = os.path.dirname(os.path.realpath(__file__))
        # 获取yaml文件路径
        yamlPath = os.path.join(curPath, "config.yaml")

    with open(yamlPath, 'r', encoding="utf-8") as f:
        # conf_dict = yaml.safe_load(f) ##这样可以直接得到结果
        content = f.read()
    conf_dict = yaml.load(stream=content, Loader=yaml.FullLoader)
    logging.debug("Load config from %s" % yamlPath)
    return conf_dict
