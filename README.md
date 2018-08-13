# qiniu_facedet_eval_tools

人脸检测评测工具

### 人脸检测

1、使用方法：

```
▶ python bk-det-eval.py -h
usage: bk-det-eval.py [-h] --gt GT --json API_RESULT

script for face detection test

optional arguments:
  -h, --help  show this help message and exit
  --gt GT     groundtruth of dataset
  --json LOG   infer result  XXX.json
```

2、文件格式

每行为一张图片对应的数据

groundtruth 行数据格式:

```
{"url": "0--Parade/0_Parade_Parade_0_628.jpg", "label": [{"data": [ {"pts": [[624, 219], [644, 219], [644, 252], [624, 252]]}], "type": "face", "name": "face"}]}

```

result 数据格式样例：

```
{
    "http://facebkt.com/Widerface/WIDER_val/images/2--Demonstration/2_Demonstration_Demonstration_Or_Protest_2_364.jpg": [
        {
            "index": 1, 
            "score": 0.9999915361404419, 
            "pts": [
                [
                    474, 
                    286
                ], 
                [
                    598, 
                    286
                ], 
                [
                    598, 
                    464
                ], 
                [
                    474, 
                    464
                ]
            ], 
            "class": "face", 
            "quality": "clear"
        }
}
```

3、代码运行

```
▶ python face-det-eval.py 
temp_ra.json recall is: 0.778, precision is: 0.905
