from functools import partial
import json
from pathlib import Path
from numpy import ndarray
from pytorch_autoencoders.config import Config
from pytorch_autoencoders.data import Dsprites
from pytorch_autoencoders.models import beta_vae, ConvVae, VariationalAutoEncoder
from pytorch_autoencoders import inference_helper, train_helper
import torch
from torch.optim import Adam


class BernoulliHead(torch.nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        shape = x.shape
        res = torch.distributions.Bernoulli(logits=x.view(shape[0] * shape[1], -1))
        return res.sample().view(shape)


def train() -> None:
    config = Config()
    config.optim = partial(Adam, lr=0.001, weight_decay=1e-5)
    config.criterion = beta_vae.get_loss_function(10.0)
    config.num_epochs = 200
    ae = ConvVae(torch.Size((64, 64)), config)

    def to_tensor(x: ndarray) -> torch.Tensor:
        return torch.tensor(x / 255.0, dtype=torch.float32).view(1, *x.shape[-2:])
    data = Dsprites(transform=to_tensor)
    loss = train_helper.train(ae, config, data)
    ae.save('dsprites_beta_vae.pth')
    path = Path('loss.json')
    path.write_str(json.dumps(loss))
    inference_helper.show_decoded_images(ae, config, data)
    inference_helper.show_feature_map(ae, config, data)


if __name__ == '__main__':
    train()
