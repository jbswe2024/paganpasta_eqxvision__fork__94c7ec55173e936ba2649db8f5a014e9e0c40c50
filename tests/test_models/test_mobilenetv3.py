import equinox as eqx
import jax
import jax.numpy as jnp
import pytest

import eqxvision.models as models


model_list = [("mobilenet_v3_small", models.mobilenet_v3_small)]


class TestMobileNetv3:
    answer = (1, 1000)

    @pytest.mark.parametrize("model_func", model_list)
    def test_mobilenet(self, model_func, demo_image, getkey):
        img = demo_image(224)

        @eqx.filter_jit
        def forward(net, x, key):
            keys = jax.random.split(key, x.shape[0])
            ans = jax.vmap(net, axis_name="batch")(x, key=keys)
            return ans

        model = model_func[1](num_classes=1000)
        output = forward(model, img, getkey())
        assert output.shape == self.answer

    @pytest.mark.parametrize("model_func", model_list)
    def test_pretrained(self, model_func, demo_image, net_preds, getkey):
        img = demo_image(224)

        @eqx.filter_jit
        def forward(net, x, key):
            keys = jax.random.split(key, x.shape[0])
            ans = jax.vmap(net, axis_name="batch")(x, key=keys)
            return ans

        model = model_func[1](pretrained=True)
        model = eqx.tree_inference(model, True)
        output = forward(model, img, getkey())

        pt_output = net_preds[model_func[0]]
        assert jnp.isclose(output, pt_output, atol=1e-4).all()
