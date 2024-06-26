# PyTorch XLNet模型 性能复现
## 目录
```
├── PrepareEnv_xlnet.sh         # 竞品PyTorch运行环境搭建  
├── README_xlnet.md             # 运行文档  
├── models                      # 提供竞品PyTorch框架的修改后的模型,官方模型请直接在脚本中拉取,统一方向的模型commit应一致,如不一致请单独在模型运行脚本中写明运行的commit  
├── run_PyTorch_xlnet.sh        # 全量竞品PyTorch框架模型运行脚本  
└── scripts/xlnet               # 提供xlnet模型复现性能的脚本
```


## 环境介绍
### 1.物理机环境
- 单机（单卡、8卡）
  - 系统：CentOS release 7.5 (Final)
  - GPU：Tesla V100-SXM2-32GB * 8
  - CPU：Intel(R) Xeon(R) Gold 6271C CPU @ 2.60GHz * 80
  - Driver Version: 460.27.04
  - 内存：629 GB
  - CUDA、cudnn Version: cuda10.1-cudnn7 、 cuda11.2-cudnn8-gcc82

### 2.Docker 镜像:
镜像使用paddle官方2.1.2镜像，与paddle测试环境相同
- **镜像版本**: `registry.baidubce.com/paddlepaddle/paddle:2.1.2-gpu-cuda10.2-cudnn7`   # 竞品镜像,每个方向的请一致
- **PyTorch 版本**: `1.8.0`  # 竞品版本：最新稳定版本，如需特定版本请备注说明原因  
- **CUDA 版本**: `10.2`
- **cuDnn 版本**: `7`


## 测试步骤
```bash
bash run_PyTorch_xlnet.sh;     # 创建容器,在该标准环境中测试模型   
```

脚本内容,如:
```bash
#!/usr/bin/env bash
# 拉镜像
ImageName="registry.baidubce.com/paddlepaddle/paddle:2.1.2-gpu-cuda10.2-cudnn7"
docker pull ${ImageName}

# 启动镜像后测试单个模型
run_cmd="bash PrepareEnv_xlnet.sh;
        cd /workspace/models/xlnet/;
        cp /workspace/scripts/xlnet/run_benchmark.sh ./;
        cp /workspace/scripts/xlnet/analysis_log.py ./;
        CUDA_VISIBLE_DEVICES=0 bash run_benchmark.sh sp 32 fp32 1000 xlnet-base-cased;
        CUDA_VISIBLE_DEVICES=0 bash run_benchmark.sh sp 128 fp32 1000 xlnet-base-cased;
        CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash run_benchmark.sh mp 32 fp32 1000 xlnet-base-cased;
        CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash run_benchmark.sh mp 128 fp32 1000 xlnet-base-cased;
        "

# 启动镜像
nvidia-docker run --name test_torch_xlnet -i  \
    --net=host \
    --shm-size=1g \
    -v $PWD:/workspace \
    ${ImageName}  /bin/bash -c "${run_cmd}"
```


## 单个模型脚本目录
```
└── models/xlnet                                   # 模型名
    ├── analysis_log.py                            # log解析脚本,每个框架尽量统一
    ├── logs                                       # 训练log,注:log中不得包含机器ip等敏感信息
    │   ├── index                                  # log解析后待入库数据json文件
    │   │   ├── nlp_xlnet_sp_bs32_fp32_1_speed     # 单卡数据
    │   │   └── nlp_xlnet_mp_bs32_fp32_8_speed     # 8卡数据
    │   └── train_log                              # 原始训练log
    └── run_benchmark.sh                           # 运行脚本（包含性能、收敛性）
```
## 输出

每个模型case需返回log解析后待入库数据json文件

```bash
{
"log_file": "/logs/pytorch1.10.0_2021.1105.031037_10.2/train_log/xlnet-base-cased_sp_bs32_fp32_1", \    # log 目录,创建规范见PrepareEnv.sh
"model_name": "nlp_xlnet-base-cased_bs32_fp32", \    # 模型case名,创建规范:repoName_模型名_bs${bs_item}_${fp_item} 如:clas_MobileNetv1_bs32_fp32
"mission_name": "语义表示", \    # 模型case所属任务名称，具体可参考scripts/config.ini
"direction_id": 1, \            # 模型case所属方向id,0:CV|1:NLP|2:Rec 具体可参考benchmark/scripts/config.ini
"run_mode": "sp", \             # 单卡:sp|多卡:mp
"index": 1, \                   # 速度验证默认为1
"gpu_num": 1, \                 # 1|8
"FINAL_RESULT": 87.389, \       # 速度计算后的平均值,需要skip掉不稳定的前几步值
"JOB_FAIL_FLAG": 0, \           # 该模型case运行0:成功|1:失败
"UNIT": "sequences/s" \         # 速度指标的单位
}
```
