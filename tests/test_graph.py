from autokeras.generator import DefaultClassifierGenerator
from autokeras.graph import *
from autokeras.net_transformer import legal_graph
from tests.common import get_conv_data, get_add_skip_model, get_conv_dense_model, get_pooling_model, \
    get_concat_skip_model


def test_conv_deeper_stub():
    graph = get_conv_dense_model()
    layer_num = graph.n_layers
    graph.to_conv_deeper_model(5, 3)

    assert graph.n_layers == layer_num + 4


def test_conv_deeper():
    graph = get_conv_dense_model()
    model = graph.produce_model()
    graph = deepcopy(graph)
    graph.to_conv_deeper_model(5, 3)
    new_model = graph.produce_model()
    input_data = torch.Tensor(get_conv_data())

    model.eval()
    new_model.eval()
    output1 = model(input_data)
    output2 = new_model(input_data)

    assert (output1 - output2).abs().sum() < 1e-1


def test_dense_deeper_stub():
    graph = get_conv_dense_model()
    graph.weighted = False
    layer_num = graph.n_layers
    graph.to_dense_deeper_model(10)

    assert graph.n_layers == layer_num + 3


def test_dense_deeper():
    graph = get_conv_dense_model()
    model = graph.produce_model()
    graph = deepcopy(graph)
    graph.to_dense_deeper_model(10)
    new_model = graph.produce_model()
    input_data = torch.Tensor(get_conv_data())

    model.eval()
    new_model.eval()
    output1 = model(input_data)
    output2 = new_model(input_data)

    assert (output1 - output2).abs().sum() < 1e-4


def test_conv_wider_stub():
    graph = get_add_skip_model()
    graph.weighted = False
    layer_num = graph.n_layers
    graph.to_wider_model(9, 3)

    assert graph.n_layers == layer_num


def test_conv_wider():
    graph = get_concat_skip_model()
    model = graph.produce_model()
    graph = deepcopy(graph)
    graph.to_wider_model(5, 3)
    new_model = graph.produce_model()
    input_data = torch.Tensor(get_conv_data())

    model.eval()
    new_model.eval()

    output1 = model(input_data)
    output2 = new_model(input_data)

    assert (output1 - output2).abs().sum() < 1e-1


def test_dense_wider_stub():
    graph = get_add_skip_model()
    graph.weighted = False
    layer_num = graph.n_layers
    graph.to_wider_model(26, 3)

    assert graph.n_layers == layer_num


def test_dense_wider():
    graph = get_add_skip_model()
    model = graph.produce_model()
    graph = deepcopy(graph)
    graph.to_wider_model(26, 3)
    new_model = graph.produce_model()
    input_data = torch.Tensor(get_conv_data())

    model.eval()
    new_model.eval()

    output1 = model(input_data)
    output2 = new_model(input_data)

    assert (output1 - output2).abs().sum() < 1e-4


def test_skip_add_over_pooling_stub():
    graph = get_pooling_model()
    graph.weighted = False
    layer_num = graph.n_layers
    graph.to_add_skip_model(1, 10)

    assert graph.n_layers == layer_num + 3


def test_skip_add_over_pooling():
    graph = get_pooling_model()
    model = graph.produce_model()
    graph = deepcopy(graph)
    graph.to_add_skip_model(1, 10)
    new_model = graph.produce_model()
    input_data = torch.Tensor(get_conv_data())

    model.eval()
    new_model.eval()

    output1 = model(input_data)
    output2 = new_model(input_data)

    assert (output1 - output2).abs().sum() < 1e-4


def test_skip_concat_over_pooling_stub():
    graph = get_pooling_model()
    graph.weighted = False
    layer_num = graph.n_layers
    graph.to_concat_skip_model(1, 14)

    assert graph.n_layers == layer_num + 3


def test_skip_concat_over_pooling():
    graph = get_pooling_model()
    model = graph.produce_model()
    graph = deepcopy(graph)
    graph.to_concat_skip_model(5, 10)
    graph.to_concat_skip_model(5, 10)
    new_model = graph.produce_model()
    input_data = torch.Tensor(get_conv_data())

    model.eval()
    new_model.eval()

    output1 = model(input_data)
    output2 = new_model(input_data)

    assert (output1 - output2).abs().sum() < 1e-4


def test_extract_descriptor_add():
    descriptor = get_add_skip_model().extract_descriptor()
    assert descriptor.n_conv == 5
    assert descriptor.n_dense == 2
    assert descriptor.skip_connections == [(2, 3, NetworkDescriptor.ADD_CONNECT), (3, 4, NetworkDescriptor.ADD_CONNECT)]


def test_extract_descriptor_concat():
    descriptor = get_concat_skip_model().extract_descriptor()
    assert descriptor.n_conv == 5
    assert descriptor.n_dense == 2
    assert descriptor.skip_connections == [(2, 3, NetworkDescriptor.CONCAT_CONNECT),
                                           (3, 4, NetworkDescriptor.CONCAT_CONNECT)]


def test_deep_layer_ids():
    graph = get_conv_dense_model()
    assert len(graph.deep_layer_ids()) == 3


def test_wide_layer_ids():
    graph = get_conv_dense_model()
    assert len(graph.wide_layer_ids()) == 2


def test_skip_connection_layer_ids():
    graph = get_conv_dense_model()
    assert len(graph.skip_connection_layer_ids()) == 1


def test_long_transform():
    graph = DefaultClassifierGenerator(10, (32, 32, 3)).generate()
    history = [('to_wider_model', 1, 256), ('to_conv_deeper_model', 1, 3),
               ('to_concat_skip_model', 6, 11)]
    for args in history:
        getattr(graph, args[0])(*list(args[1:]))
        graph.produce_model()
    assert legal_graph(graph)
