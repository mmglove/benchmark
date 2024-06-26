#   Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from common_import import *
from pad2d import PaddlePad2d, TorchPad2d


@benchmark_registry.register("pad3d", reuse="pad2d")
class Pad3dConfig(APIConfig):
    def __init__(self):
        super(Pad3dConfig, self).__init__('pad3d')

    def init_from_json(self, filename, config_id=0, unknown_dim=16):
        super(Pad3dConfig, self).init_from_json(filename, config_id,
                                                unknown_dim)
        # in API 'torch.nn.functional.pad()', 'reflect' mode is not implemented,
        # while in API 'torch.nn.ReplicationPad3d()', the logic of 'reflection' 
        # mode is different from paddle.pad(mode='reflect')
        # So set run_torch as False when using 'reflect' mode
        if self.mode == "reflect":
            print(
                "Warning:\n"
                "  1. 'reflect' mode in torch.nn.functional.pad is not implemented.\n"
            )
            self.run_torch = False
        if len(self.x_shape) != 5:
            print("Warning:\n"
                  "  2. The dimentions of the input has to be 5.\n")


@benchmark_registry.register("pad3d")
class TFPad3d(TensorflowOpBenchmarkBase):
    def build_graph(self, config):
        padding = [
            [0, 0],
            [0, 0],
            [config.pad[4], config.pad[5]],
            [config.pad[2], config.pad[3]],
            [config.pad[0], config.pad[1]],
        ]
        x = self.variable(name='x', shape=config.x_shape, dtype=config.x_dtype)
        out = tf.pad(x,
                     padding,
                     mode=str.upper(config.mode),
                     constant_values=config.value)

        self.feed_list = [x]
        self.fetch_list = [out]
        if config.backward:
            self.append_gradients(out, [x])
