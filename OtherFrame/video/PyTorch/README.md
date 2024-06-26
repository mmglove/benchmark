# TimeSformer PyTorch 性能复现
## 目录 

├── PrepareEnv.sh   # 竞品PyTorch运行环境搭建  
├── README.md       # 运行文档  
├── run_PyTorch.sh  # 全量竞品PyTorch框架模型运行脚本  
├── models          # 提供竞品PyTorch框架的修改后的模型,官方模型请直接在脚本中拉取,统一方向的模型commit应一致,如不一致请单独在模型运行脚本中写明运行的commit  
└── scripts         # 提供各个模型复现性能的脚本  
## 环境介绍
### 1.物理机环境
- 单机（单卡、8卡）
  - 系统：Ubuntu 16.04.7 LT
  - GPU：Tesla V100-SXM2-32GB * 8
  - CPU：Intel(R) Xeon(R) Gold 6271C CPU @ 2.60GHz * 80
  - Driver Version: 460.27.04
  - 内存：629 GB
  - CUDA、cudnn Version: cuda10.2-cudnn7
- 多机（32卡） TODO
### 2.Docker 镜像,如:

- **镜像版本**: `hub.baidubce.com/paddlepaddle/paddle:latest-dev-cuda10.2-cudnn7-gcc82`   # 竞品镜像,每个方向的请一致
- **PyTorch 版本**: `1.8.0`  # 竞品版本：最新稳定版本，如需特定版本请备注说明原因  
- **CUDA 版本**: `10.2`
- **cuDnn 版本**: `7.6.5`

## 测试步骤
```bash
bash run_PyTorch.sh;     # 创建容器,在该标准环境中测试模型   
```
脚本内容,如:
```bash
# 提交内容 #
ImageName="registry.baidubce.com/paddlepaddle/paddle:2.1.2-gpu-cuda10.2-cudnn7";
docker pull ${ImageName}
export BENCHMARK_ROOT=/workspace # 对应实际地址 benchmark/OtherFrameworks/video/PyTorch

run_cmd="bash PrepareEnv.sh
        cd ${BENCHMARK_ROOT}/models/TimeSformer;
        cp ${BENCHMARK_ROOT}/scripts/TimeSformer/run_benchmark.sh ./;
        cp ${BENCHMARK_ROOT}/scripts/TimeSformer/analysis_log.py ./;
        cp ${BENCHMARK_ROOT}/scripts/TimeSformer/preData.sh ./;
        bash preData.sh;

        CUDA_VISIBLE_DEVICES=0 bash run_benchmark.sh sp 1 fp32 TimeSformer;
        sleep 60;

        CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash run_benchmark.sh mp 1 fp32 TimeSformer;
        sleep 60;

        CUDA_VISIBLE_DEVICES=0 bash run_benchmark.sh sp 14 fp32 TimeSformer;
        sleep 60;

        CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash run_benchmark.sh mp 14 fp32 TimeSformer;
        sleep 60;
        "

nvidia-docker run --name test_torch_video -it  \
    --net=host \
    --shm-size=64g \
    -v $PWD:/workspace \
    ${ImageName}  /bin/bash -c "${run_cmd}"

nvidia-docker stop test_torch_video
nvidia-docker rm test_torch_video

```
## 单个模型脚本目录

TimeSformer                # 模型名  
├── README.md              # 运行文档  
├── analysis_log.py        # log解析脚本,每个框架尽量统一,可参考[paddle的analysis.py](https://github.com/mmglove/benchmark/blob/jp_0907/scripts/analysis.py)  
├── logs                   # 训练log,注:log中不得包含机器ip等敏感信息  
│   ├── index              # log解析后待入库数据json文件   
│   │   ├── TimeSformer_sp_bs1_fp32_1_speed  # 单卡数据  
│   │   ├── TimeSformer_mp_bs1_fp32_8_speed  # 8卡数据  
│   │   ├── TimeSformer_sp_bs14_fp32_1_speed  # 单卡数据  
│   │   └── TimeSformer_mp_bs14_fp32_8_speed  # 8卡数据  
│   └── train_log          # 原始训练log 
│       ├── TimeSformer_sp_bs1_fp32_1 # 单卡数据
        ├── TimeSformer_mp_bs1_fp32_8 # 8卡数据
        ├── TimeSformer_sp_bs14_fp32_1  # 单卡数据
        └── TimeSformer_mp_bs14_fp32_8  # 8卡数据
├── preData.sh             # 数据处理  
└── run_benchmark.sh       # 运行脚本（包含性能、收敛性）  

## 输出

每个模型case需返回log解析后待入库数据json文件

```bash
{
"log_file": "/workspace/scripts/logs/train_log/TimeSformer_sp_bs1_fp32_1", \    # log 目录,创建规范见PrepareEnv.sh 
"model_name": "video_TimeSformer_bs1_fp32", \    # 模型case名,创建规范:repoName_模型名_bs${bs_item}_${fp_item} 如:clas_MobileNetv1_bs32_fp32
"mission_name": "视频分类", \     # 模型case所属任务名称，具体可参考scripts/config.ini      
"direction_id": 0, \            # 模型case所属方向id,0:CV|1:NLP|2:Rec 具体可参考benchmark/scripts/config.ini    
"run_mode": "sp", \             # 单卡:sp|多卡:mp
"index": 1, \                   # 速度验证默认为1
"gpu_num": 1, \                 # 1|8
"FINAL_RESULT": 7.057693427777956, \      # 速度计算后的平均值,需要skip掉不稳定的前几步值
"JOB_FAIL_FLAG": 0, \           # 该模型case运行0:成功|1:失败
"UNIT": "videos/sec" \            # 速度指标的单位 
}

```



