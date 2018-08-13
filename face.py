# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import json
import requests
import os
from ava_auth import AuthFactory
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
lock=Lock()

# privat dan
ak = "access key"
sk = "secret key"

n_thread=20
log_list={}
face_list=[]


def parser():
    parser = ArgumentParser('face detect')

    parser.add_argument('--img_file','-i',dest='img_file',
                        default='./temp.txt',type=str)

    parser.add_argument('--dst','-d',dest='dst_file',
                        default='./out_ra/face_ra1.lst',type=str)

    parser.add_argument('--log','-l',dest='log',
                        default='./temp_ra.json',type=str)

    parser.add_argument('--num_thread','-n',dest='num_thread',
                        default=20,type=int)

    parser.add_argument('--host','-o',dest='host',
                    default='',type=str)
    return parser.parse_args()


def url_gen(url_base,file):
    with open(file,'r') as f:
        lines=f.readlines()
        for line in lines:
            line=line.strip('\n')
            yield os.path.join(url_base,line)


def token_gen(ak,sk):
    factory = AuthFactory(ak,sk)
    fauth = factory.get_qiniu_auth
    token=fauth()
    return token


def face(response):
    r=response
    return True if (r['code']==200 and r["result"]["detections"]) else False


def request(url):
    body=json.dumps({"data": {"uri": url}})
    token=token_gen(ak,sk)
    try:
	print 'request suessfully'
        r=requests.post('http://serve.atlab.ai/v1/eval/facex-detect', data=body,timeout=5, headers={"Content-Type": "application/json"}, auth=token)
    except Exception as e:
        with lock:
            print("http Exception: %s"%e)
    else:
        if r.status_code==200:
            with lock:
                r=r.json()
                print(url)
                log_list[url]=r["result"]["detections"] if r['code']==200 else ""
                if face(r):
                    face_list.append(url)

def write_log(logfile,log_list):
    with open(logfile,'w') as f_log:
        json.dump(log_list, f_log, indent=4)

def write_file(dst,face_list):
    with open(dst,'w') as f:
        for face in face_list:
            f.writelines(str(face)+'\n')

if __name__=='__main__':
    args = parser()

    urls=url_gen(args.host,args.img_file)
    with ThreadPoolExecutor(max_workers=n_thread) as executor:
        executor.map(request,urls)
    write_file(args.dst_file,face_list)
    write_log(args.log,log_list)
