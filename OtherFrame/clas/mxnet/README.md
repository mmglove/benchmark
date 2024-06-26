## 目录 

├── README.md       # 运行文档  
├── models          # 提供竞品Mxnet框架的修改后的模型,官方模型请直接在脚本中拉取,统一方向的模型commit应一致,如不一致请单独在模型运行脚本中写明运行的commit  
├── run_mxnet.sh  # 全量竞品mxnet框架模型运行脚本  
└── scripts         # 提供各个模型复现性能的脚本  
## 环境介绍
### 1.物理机环境
- 单机（单卡、8卡）
  - 系统：CentOS release 7.5 (Final)
  - GPU：Tesla V100-SXM2-32GB * 8
  - CPU：Intel(R) Xeon(R) Gold 6271C CPU @ 2.60GHz * 80
  - Driver Version: 460.27.04
  - 内存：629 GB
  - CUDA、cudnn Version: cuda10.1-cudnn7 、 cuda11.2-cudnn8-gcc82
- 多机（32卡） TODO
### 2.Docker 镜像,如:

- **镜像版本**: `registry.baidubce.com/paddlepaddle/paddle:2.1.2-gpu-cuda10.2-cudnn7`   # mxnet 官方没有提供最新mxnet版本镜像，使用paddle镜像，自己安装环境
- **mxnet-cu102 版本**: `1.8.0`  # 竞品版本：最新稳定版本，如需特定版本请备注说明原因  
- **CUDA 版本**: `10.2`
- **cuDnn 版本**: `8.2.4`

## 测试步骤
**注意**：由于使用demo数据，测试速度可能受影响，最好使用完整ImageNet完整数据集进行测试。
          同时，由于mxnet官方不提供最新的mxnet的官方镜像，使用paddle镜像会报cudnn相关bug。测试时cudnn需要自己手动安装
```bash
bash run_mxnet.sh;     # 创建容器,在该标准环境中测试模型   
```
脚本内容,如:
```bash
#!/usr/bin/env bash
# 拉镜像
ImageName="registry.baidubce.com/paddlepaddle/paddle:2.1.2-gpu-cuda10.2-cudnn7";
docker pull ${ImageName}
# 启动镜像后测试MobileNetV1
run_cmd="
        cd /workspace/models/gluon-cv/;
        cp /workspace/scripts/*.sh ./;
        cp /workspace/scripts/analysis_log.py ./;
        bash PrepareEnv.sh #请详看shell脚本,可能需要手动执行
        bash PrepareData.sh;
        CUDA_VISIBLE_DEVICES=0 bash run_benchmark.sh sp 64 fp32 500 mobilenet1.0;
        CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash run_benchmark.sh mp 64 fp32 500 mobilenet1.0;
        CUDA_VISIBLE_DEVICES=0 bash run_benchmark.sh sp 768 fp32 500 mobilenet1.0;
        CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash run_benchmark.sh mp 768 fp32 500 mobilenet1.0;
        mv clas* /workspace/
        "
# 启动镜像
nvidia-docker run --name test_mxnet -it  \
    --net=host \
    --shm-size=1g \
    -v $PWD:/workspace \
    ${ImageName}  /bin/bash -c "${run_cmd}"
nvidia-docker stop test_mxnet
nvidia-docker rm test_mxnet
```

## 输出

每个模型case需返回log解析后待入库数据json文件

```bash
{
"log_file": "clas_MobileNetV1_mp_bs64_fp32_8_speed", \   
"model_name": "clas_MobileNetv1_bs32_fp32", \    # 模型case名,创建规范:repoName_模型名_bs${bs_item}_${fp_item} 如:clas_MobileNetv1_bs32_fp32
"mission_name": "图像分类", \     # 模型case所属任务名称，具体可参考scripts/config.ini      
"direction_id": 0, \            # 模型case所属方向id,0:CV|1:NLP|2:Rec 具体可参考benchmark/scripts/config.ini    
"run_mode": "sp", \             # 单卡:sp|多卡:mp
"index": 1, \                   # 速度验证默认为1
"gpu_num": 1, \                 # 1|8
"FINAL_RESULT": 197.514, \      # 速度计算后的平均值,需要skip掉不稳定的前几步值
"JOB_FAIL_FLAG": 0, \           # 该模型case运行0:成功|1:失败
"UNIT": "images/s" \            # 速度指标的单位 
}

```
