import seisbench.models
from seisbench.models.base import ActivationLSTMCell, CustomLSTM

import numpy as np
import obspy
from obspy import UTCDateTime
import torch
from unittest.mock import patch
import logging
import pytest


def test_weights_docstring():
    model = seisbench.models.GPD()
    assert model.weights_docstring is None

    model = seisbench.models.GPD.from_pretrained("dummy")
    assert isinstance(model.weights_docstring, str)


def test_has_mismatching_records():
    t0 = UTCDateTime(0)
    stats = {
        "network": "SB",
        "station": "TEST",
        "channel": "HHZ",
        "sampling_rate": 100,
        "starttime": t0,
    }

    trace0 = obspy.Trace(np.zeros(1000), stats)
    trace1 = obspy.Trace(np.ones(1000), stats)

    # Overlapping matching
    stream = obspy.Stream([trace0.slice(t0, t0 + 10), trace0.slice(t0 + 5, t0 + 15)])
    assert not seisbench.models.WaveformModel.has_mismatching_records(stream)

    # Overlapping not matching
    stream = obspy.Stream([trace0.slice(t0, t0 + 10), trace1.slice(t0 + 5, t0 + 15)])
    assert seisbench.models.WaveformModel.has_mismatching_records(stream)

    # Full intersection matching
    stream = obspy.Stream([trace0.slice(t0, t0 + 15), trace0.slice(t0 + 5, t0 + 10)])
    assert not seisbench.models.WaveformModel.has_mismatching_records(stream)

    # Full intersection not matching
    stream = obspy.Stream([trace0.slice(t0, t0 + 15), trace1.slice(t0 + 5, t0 + 10)])
    assert seisbench.models.WaveformModel.has_mismatching_records(stream)

    # No intersection matching
    stream = obspy.Stream([trace0.slice(t0, t0 + 10), trace0.slice(t0 + 15, t0 + 20)])
    assert not seisbench.models.WaveformModel.has_mismatching_records(stream)

    # No intersection not matching
    stream = obspy.Stream([trace0.slice(t0, t0 + 10), trace1.slice(t0 + 15, t0 + 20)])
    assert not seisbench.models.WaveformModel.has_mismatching_records(stream)

    # Three traces matching
    stream = obspy.Stream(
        [
            trace0.slice(t0, t0 + 10),
            trace0.slice(t0 + 5, t0 + 15),
            trace0.slice(t0 + 7, t0 + 11),
        ]
    )
    assert not seisbench.models.WaveformModel.has_mismatching_records(stream)

    # Three traces not matching
    stream = obspy.Stream(
        [
            trace0.slice(t0, t0 + 10),
            trace0.slice(t0 + 5, t0 + 15),
            trace1.slice(t0 + 7, t0 + 11),
        ]
    )
    assert seisbench.models.WaveformModel.has_mismatching_records(stream)


class DummyWaveformModel(seisbench.models.WaveformModel):
    def annotate(self, stream, *args, **kwargs):
        pass

    def classify(self, stream, *args, **kwargs):
        pass

    @property
    def device(self):
        return "cpu"


def test_stream_to_arrays():
    t0 = UTCDateTime(0)
    stats_z = {
        "network": "SB",
        "station": "TEST",
        "channel": "HHZ",
        "sampling_rate": 100,
        "starttime": t0,
    }
    stats_n = {
        "network": "SB",
        "station": "TEST",
        "channel": "HHN",
        "sampling_rate": 100,
        "starttime": t0,
    }
    stats_e = {
        "network": "SB",
        "station": "TEST",
        "channel": "HHE",
        "sampling_rate": 100,
        "starttime": t0,
    }
    dummy = DummyWaveformModel(component_order="ZNE")

    trace_z = obspy.Trace(np.ones(1000), stats_z)
    trace_n = obspy.Trace(2 * np.ones(1000), stats_n)
    trace_e = obspy.Trace(3 * np.ones(1000), stats_e)

    # Aligned strict
    stream = obspy.Stream([trace_z, trace_n, trace_e])
    times, data = dummy.stream_to_arrays(stream, strict=True)
    assert len(times) == len(data) == 1
    assert times[0] == t0
    assert data[0].shape == (3, len(trace_z.data))
    assert (data[0][0] == trace_z.data).all()
    assert (data[0][1] == trace_n.data).all()
    assert (data[0][2] == trace_e.data).all()

    # Aligned non strict
    stream = obspy.Stream([trace_z, trace_n, trace_e])
    times, data = dummy.stream_to_arrays(stream, strict=False)
    assert len(times) == len(data) == 1
    assert times[0] == t0
    assert data[0].shape == (3, len(trace_z.data))
    assert (data[0][0] == trace_z.data).all()
    assert (data[0][1] == trace_n.data).all()
    assert (data[0][2] == trace_e.data).all()

    # Covering strict
    stream = obspy.Stream([trace_z, trace_n, trace_e.slice(t0 + 1, t0 + 5)])
    times, data = dummy.stream_to_arrays(stream, strict=True)
    assert len(times) == len(data) == 1
    assert times[0] == t0 + 1
    assert data[0].shape == (3, 401)
    assert (data[0][0] == trace_z.data[0]).all()
    assert (data[0][1] == trace_n.data[0]).all()
    assert (data[0][2] == trace_e.data[0]).all()

    # Covering non-strict
    stream = obspy.Stream([trace_z, trace_n, trace_e.slice(t0 + 1, t0 + 5)])
    times, data = dummy.stream_to_arrays(stream, strict=False)
    assert len(times) == len(data) == 1
    assert times[0] == t0
    assert data[0].shape == (3, len(trace_z.data))
    assert (data[0][0] == trace_z.data[0]).all()
    assert (data[0][1] == trace_n.data[0]).all()
    assert (data[0][2, 100:501] == trace_e.data[0]).all()
    assert (data[0][2, :100] == 0).all()
    assert (data[0][2, 501:] == 0).all()

    # Double covering strict
    stream = obspy.Stream(
        [trace_z, trace_n, trace_e.slice(t0 + 1, t0 + 5), trace_e.slice(t0 + 6, t0 + 8)]
    )
    times, data = dummy.stream_to_arrays(stream, strict=True)
    assert len(times) == len(data) == 2
    assert times[0] == t0 + 1
    assert times[1] == t0 + 6
    assert data[0].shape == (3, 401)
    assert data[1].shape == (3, 201)
    for i in range(2):
        assert (data[i][0] == trace_z.data[0]).all()
        assert (data[i][1] == trace_n.data[0]).all()
        assert (data[i][2] == trace_e.data[0]).all()

    # Double covering non strict
    stream = obspy.Stream(
        [trace_z, trace_n, trace_e.slice(t0 + 1, t0 + 5), trace_e.slice(t0 + 6, t0 + 8)]
    )
    times, data = dummy.stream_to_arrays(stream, strict=False)
    assert len(times) == len(data) == 1
    assert times[0] == t0
    assert data[0].shape == (3, len(trace_z.data))
    assert (data[0][0] == trace_z.data[0]).all()
    assert (data[0][1] == trace_n.data[0]).all()
    assert (data[0][2, 100:501] == trace_e.data[0]).all()
    assert (data[0][2, 600:801] == trace_e.data[0]).all()
    assert (data[0][2, :100] == 0).all()
    assert (data[0][2, 501:600] == 0).all()
    assert (data[0][2, 801:] == 0).all()

    # Intersecting strict
    stream = obspy.Stream(
        [trace_z, trace_n.slice(t0 + 1, t0 + 5), trace_e.slice(t0 + 3, t0 + 7)]
    )
    times, data = dummy.stream_to_arrays(stream, strict=True)
    assert len(times) == len(data) == 1
    assert times[0] == t0 + 3
    assert data[0].shape == (3, 201)
    assert (data[0][0] == trace_z.data[0]).all()
    assert (data[0][1] == trace_n.data[0]).all()
    assert (data[0][2] == trace_e.data[0]).all()

    # Intersecting non strict
    stream = obspy.Stream(
        [trace_z, trace_n.slice(t0 + 1, t0 + 5), trace_e.slice(t0 + 3, t0 + 7)]
    )
    times, data = dummy.stream_to_arrays(stream, strict=False)
    assert len(times) == len(data) == 1
    assert times[0] == t0
    assert data[0].shape == (3, len(trace_z.data))
    assert (data[0][0] == trace_z.data[0]).all()
    assert (data[0][1, 100:501] == trace_n.data[0]).all()
    assert (data[0][1, :100] == 0).all()
    assert (data[0][1, 501:] == 0).all()
    assert (data[0][2, 300:701] == trace_e.data[0]).all()
    assert (data[0][2, :300] == 0).all()
    assert (data[0][2, 701:] == 0).all()

    # No overlap strict
    stream = obspy.Stream(
        [
            trace_z.slice(t0, t0 + 1),
            trace_n.slice(t0 + 1, t0 + 2),
            trace_e.slice(t0 + 1, t0 + 2),
        ]
    )
    times, data = dummy.stream_to_arrays(stream, strict=True)
    assert len(times) == len(data) == 0

    # No overlap non strict
    stream = obspy.Stream(
        [
            trace_z.slice(t0, t0 + 1),
            trace_n.slice(t0 + 1, t0 + 2),
            trace_e.slice(t0 + 1, t0 + 2),
        ]
    )
    times, data = dummy.stream_to_arrays(stream, strict=False)
    assert len(times) == len(data) == 1
    assert times[0] == t0
    assert data[0].shape == (3, 201)
    assert (data[0][0, :101] == trace_z.data[0]).all()
    assert (data[0][0, 101:] == 0).all()
    assert (data[0][1, :100] == 0).all()
    assert (data[0][1, 100:] == trace_n.data[0]).all()
    assert (data[0][2, :100] == 0).all()
    assert (data[0][2, 100:] == trace_e.data[0]).all()

    # Separate fragments strict
    stream = obspy.Stream(
        [
            trace_z.slice(t0, t0 + 1),
            trace_n.slice(t0 + 0, t0 + 1),
            trace_e.slice(t0 + 0, t0 + 1),
            trace_z.slice(t0 + 2, t0 + 3),
            trace_n.slice(t0 + 2, t0 + 3),
            trace_e.slice(t0 + 2, t0 + 3),
        ]
    )
    times, data = dummy.stream_to_arrays(stream, strict=True)
    assert len(times) == len(data) == 2
    for i in range(2):
        assert times[i] == t0 + 2 * i
        assert data[i].shape == (3, 101)
        assert (data[i][0] == trace_z.data[0]).all()
        assert (data[i][1] == trace_n.data[0]).all()
        assert (data[i][2] == trace_e.data[0]).all()

    # Separate fragments non-strict
    stream = obspy.Stream(
        [
            trace_z.slice(t0, t0 + 1),
            trace_n.slice(t0 + 0, t0 + 1),
            trace_e.slice(t0 + 0, t0 + 1),
            trace_z.slice(t0 + 2, t0 + 3),
            trace_n.slice(t0 + 2, t0 + 3),
            trace_e.slice(t0 + 2, t0 + 3),
        ]
    )
    times, data = dummy.stream_to_arrays(stream, strict=False)
    assert len(times) == len(data) == 2
    for i in range(2):
        assert times[i] == t0 + 2 * i
        assert data[i].shape == (3, 101)
        assert (data[i][0] == trace_z.data[0]).all()
        assert (data[i][1] == trace_n.data[0]).all()
        assert (data[i][2] == trace_e.data[0]).all()


def test_flexible_horizontal_components(caplog):
    t0 = UTCDateTime(0)
    stats_z = {
        "network": "SB",
        "station": "TEST",
        "channel": "HHZ",
        "sampling_rate": 100,
        "starttime": t0,
    }
    stats_n = {
        "network": "SB",
        "station": "TEST",
        "channel": "HHN",
        "sampling_rate": 100,
        "starttime": t0,
    }
    stats_e = {
        "network": "SB",
        "station": "TEST",
        "channel": "HHE",
        "sampling_rate": 100,
        "starttime": t0,
    }
    stats_1 = {
        "network": "SB",
        "station": "TEST",
        "channel": "HH1",
        "sampling_rate": 100,
        "starttime": t0,
    }
    stats_2 = {
        "network": "SB",
        "station": "TEST",
        "channel": "HH2",
        "sampling_rate": 100,
        "starttime": t0,
    }
    stats_2_test2 = {
        "network": "SB",
        "station": "TEST2",
        "channel": "HH2",
        "sampling_rate": 100,
        "starttime": t0,
    }
    dummy = DummyWaveformModel(component_order="ZNE")

    trace_z = obspy.Trace(np.ones(1000), stats_z)
    trace_n = obspy.Trace(2 * np.ones(1000), stats_n)
    trace_e = obspy.Trace(3 * np.ones(1000), stats_e)
    trace_1 = obspy.Trace(4 * np.ones(1000), stats_1)
    trace_2 = obspy.Trace(5 * np.ones(1000), stats_2)
    trace_2_test2 = obspy.Trace(5 * np.ones(1000), stats_2_test2)

    # flexible_horizontal_components=False
    stream = obspy.Stream([trace_z, trace_1, trace_2])
    times, data = dummy.stream_to_arrays(
        stream, strict=True, flexible_horizontal_components=False
    )
    assert len(times) == len(data) == 0

    # flexible_horizontal_components=True
    stream = obspy.Stream([trace_z, trace_1, trace_2])
    times, data = dummy.stream_to_arrays(
        stream, strict=True, flexible_horizontal_components=True
    )
    assert len(times) == len(data) == 1

    # Warning for mixed component names
    caplog.clear()
    stream = obspy.Stream([trace_z, trace_n, trace_e, trace_1, trace_2])
    with caplog.at_level(logging.WARNING):
        times, data = dummy.stream_to_arrays(
            stream, strict=True, flexible_horizontal_components=True
        )
    assert "This might lead to undefined behavior." in caplog.text
    assert len(times) == len(data) == 1

    # No warning for mixed component names on different stations
    caplog.clear()
    stream = obspy.Stream([trace_z, trace_n, trace_e, trace_2_test2])
    with caplog.at_level(logging.WARNING):
        dummy.stream_to_arrays(stream, strict=True, flexible_horizontal_components=True)
    assert "This might lead to undefined behavior." not in caplog.text


def test_group_stream_by_instrument():
    # The first 3 should be grouped together, the last 3 should each be separate
    stream = obspy.Stream(
        [
            obspy.Trace(header={"network": "SB", "station": "ABC1", "channel": "BHZ"}),
            obspy.Trace(header={"network": "SB", "station": "ABC1", "channel": "BHN"}),
            obspy.Trace(header={"network": "SB", "station": "ABC1", "channel": "BHE"}),
            obspy.Trace(header={"network": "SB", "station": "ABC1", "channel": "HHZ"}),
            obspy.Trace(header={"network": "HB", "station": "ABC1", "channel": "BHZ"}),
            obspy.Trace(header={"network": "SB", "station": "ABC2", "channel": "BHZ"}),
        ]
    )

    dummy = DummyWaveformModel(component_order="ZNE")
    groups = dummy.groups_stream_by_instrument(stream)

    assert len(groups) == 4
    assert list(sorted([len(x) for x in groups])) == [1, 1, 1, 3]


def test_recursive_torch_to_numpy():
    dummy = DummyWaveformModel(component_order="ZNE")

    x = np.random.rand(5, 3)
    y = dummy._recursive_torch_to_numpy(torch.tensor(x))
    assert (x == y).all()

    xt = torch.tensor(x)
    bigtest = [[xt, xt, xt], (xt, xt, xt, xt)]
    bigresult = dummy._recursive_torch_to_numpy(bigtest)
    assert len(bigresult) == 2
    assert isinstance(bigresult, list)
    assert len(bigresult[0]) == 3
    assert isinstance(bigresult[0], list)
    assert len(bigresult[1]) == 4
    assert isinstance(bigresult[1], tuple)


def test_recursive_slice_pred():
    dummy = DummyWaveformModel(component_order="ZNE")

    x1 = np.random.rand(5, 3)
    x2 = np.random.rand(5, 3)
    x3 = np.random.rand(5, 3)
    x4 = np.random.rand(5, 3)
    x5 = np.random.rand(5, 3)

    x = [[x1, x2], (x3, x4, x5)]
    y = dummy._recursive_slice_pred(x)

    for i in range(x1.shape[0]):
        assert isinstance(y[i], list)
        assert isinstance(y[i][0], list)
        assert isinstance(y[i][1], tuple)

        [px1, px2], (px3, px4, px5) = y[i]
        assert (x1[i] == px1).all()
        assert (x2[i] == px2).all()
        assert (x3[i] == px3).all()
        assert (x4[i] == px4).all()
        assert (x5[i] == px5).all()


def test_trim_nan():
    dummy = DummyWaveformModel(component_order="ZNE")

    x = np.random.rand(100)
    y, f, b = dummy._trim_nan(x)
    assert (y == x).all()
    assert (f, b) == (0, 0)

    x[:10] = np.nan
    y, f, b = dummy._trim_nan(x)
    assert (y == x[10:]).all()
    assert (f, b) == (10, 0)

    x[95:] = np.nan
    y, f, b = dummy._trim_nan(x)
    assert (y == x[10:95]).all()
    assert (f, b) == (10, 5)

    x[30:40] = np.nan
    y, f, b = dummy._trim_nan(x)
    # Needs an extra check as nan==nan is defined as false
    double_nan = np.logical_and(np.isnan(y), np.isnan(x[10:95]))
    assert (np.logical_or(y == x[10:95], double_nan)).all()
    assert (f, b) == (10, 5)


def test_predictions_to_stream():
    dummy = DummyWaveformModel(component_order="ZNE")

    pred_rates = [100, 50]
    pred_times = [UTCDateTime(), UTCDateTime()]
    preds = [np.random.rand(1000, 3), np.random.rand(2000, 3)]
    preds[0][:100] = np.nan  # Test proper shift
    trace = obspy.Trace(np.zeros(100), header={"network": "SB", "station": "ABC1"})

    stream = dummy._predictions_to_stream(pred_rates, pred_times, preds, trace)

    assert stream[0].stats.starttime == pred_times[0] + 1
    assert stream[1].stats.starttime == pred_times[0] + 1
    assert stream[2].stats.starttime == pred_times[0] + 1
    assert stream[3].stats.starttime == pred_times[1]
    assert stream[4].stats.starttime == pred_times[1]
    assert stream[5].stats.starttime == pred_times[1]

    assert stream[0].id == "SB.ABC1..DummyWaveformModel_0"
    assert stream[1].id == "SB.ABC1..DummyWaveformModel_1"
    assert stream[2].id == "SB.ABC1..DummyWaveformModel_2"
    assert stream[3].id == "SB.ABC1..DummyWaveformModel_0"
    assert stream[4].id == "SB.ABC1..DummyWaveformModel_1"
    assert stream[5].id == "SB.ABC1..DummyWaveformModel_2"

    assert stream[0].stats.sampling_rate == 100
    assert stream[1].stats.sampling_rate == 100
    assert stream[2].stats.sampling_rate == 100
    assert stream[3].stats.sampling_rate == 50
    assert stream[4].stats.sampling_rate == 50
    assert stream[5].stats.sampling_rate == 50


def test_annotate_point():
    dummy = DummyWaveformModel(
        component_order="ZNE", in_samples=1000, sampling_rate=100
    )
    times = [0]
    data = [np.ones((3, 10000))]
    with patch(
        "seisbench.models.WaveformModel._predict_and_postprocess_windows"
    ) as predict_func:
        predict_func.return_value = 91 * [0]
        pred_times, pred_rates, full_preds = dummy._annotate_point(
            times, data, {"stride": 100, "sampling_rate": 100}
        )
        argdict, fragments = predict_func.call_args[0]

    assert fragments.shape == (91, 3, 1000)
    assert len(pred_times) == len(pred_rates) == len(full_preds) == 1
    assert full_preds[0].shape == (91, 1)
    assert pred_rates[0] == 1


def test_annotate_array():
    dummy = DummyWaveformModel(
        component_order="ZNE", in_samples=1000, sampling_rate=100, pred_sample=(0, 1000)
    )
    times = [0]
    data = [np.ones((3, 10001))]
    with patch(
        "seisbench.models.WaveformModel._predict_and_postprocess_windows"
    ) as predict_func:
        predict_func.return_value = 12 * [np.ones((1000, 3))]
        pred_times, pred_rates, full_preds = dummy._annotate_array(
            times, data, {"overlap": 100, "sampling_rate": 100}
        )
        argdict, fragments = predict_func.call_args[0]

    assert fragments.shape == (12, 3, 1000)
    assert len(pred_times) == len(pred_rates) == len(full_preds) == 1
    assert full_preds[0].shape == (10001, 3)
    assert pred_rates[0] == 100.0


def test_picks_from_annotations():
    data = np.zeros(1000)
    data[100:201] = 0.7
    data[300:401] = 0.1
    data[500:701] = 0.5
    data[600] = 0.6  # Different peak
    t0 = UTCDateTime()
    trace = obspy.Trace(
        data,
        header={
            "network": "SB",
            "station": "ABC1",
            "starttime": t0,
            "sampling_rate": 100,
        },
    )

    picks = seisbench.models.WaveformModel.picks_from_annotations(
        obspy.Stream([trace]), 0.3, "P"
    )
    picks = sorted(picks)

    assert len(picks) == 2

    assert picks[0].trace_id == "SB.ABC1."
    assert picks[0].start_time == t0 + 1
    assert picks[0].end_time == t0 + 2
    assert picks[0].peak_value == 0.7
    assert picks[0].phase == "P"

    assert picks[1].trace_id == "SB.ABC1."
    assert picks[1].start_time == t0 + 5
    assert picks[1].end_time == t0 + 7
    assert picks[1].peak_time == t0 + 6
    assert picks[1].peak_value == 0.6
    assert picks[1].phase == "P"


def test_detections_from_annotations():
    data = np.zeros(1000)
    data[100:201] = 0.7
    data[300:401] = 0.1
    data[500:701] = 0.5
    data[600] = 0.6  # Different peak
    t0 = UTCDateTime()
    trace = obspy.Trace(
        data,
        header={
            "network": "SB",
            "station": "ABC1",
            "starttime": t0,
            "sampling_rate": 100,
        },
    )

    detections = seisbench.models.WaveformModel.detections_from_annotations(
        obspy.Stream([trace]), 0.3
    )
    detections = sorted(detections)

    assert len(detections) == 2

    assert detections[0].trace_id == "SB.ABC1."
    assert detections[0].start_time == t0 + 1
    assert detections[0].end_time == t0 + 2
    assert detections[0].peak_value == 0.7

    assert detections[1].trace_id == "SB.ABC1."
    assert detections[1].start_time == t0 + 5
    assert detections[1].end_time == t0 + 7
    assert detections[1].peak_value == 0.6


def test_waveform_pipeline_instantiation():
    with pytest.raises(TypeError):
        seisbench.models.WaveformPipeline({})

    class MyPipeline(seisbench.models.WaveformPipeline):
        def annotate(self, stream, **kwargs):
            pass

        def classify(self, stream, **kwargs):
            pass

        @classmethod
        def component_classes(cls):
            return {}

    MyPipeline({})


def test_waveform_pipeline_list_pretrained(tmp_path):
    class MyPipeline(seisbench.models.WaveformPipeline):
        def annotate(self, stream, **kwargs):
            pass

        def classify(self, stream, **kwargs):
            pass

        @classmethod
        def component_classes(cls):
            return {}

    def write_config(*arg, **kwargs):
        path = tmp_path / "pipelines" / "mypipeline" / "myconfig.json"
        with open(path, "w") as f:
            f.write('{"docstring": "test docstring"}\n')

    with patch(
        "seisbench.cache_root", tmp_path
    ):  # Ensure test does not modify SeisBench cache
        with patch("seisbench.util.ls_webdav") as ls_webdav:
            ls_webdav.return_value = ["myconfig.json"]
            with patch("seisbench.util.download_http") as download_http:
                download_http.side_effect = write_config

                configurations = MyPipeline.list_pretrained(details=True)
                assert configurations == {"myconfig": "test docstring"}


def test_waveform_pipeline_from_pretrained(tmp_path):
    class MyPipeline(seisbench.models.WaveformPipeline):
        def annotate(self, stream, **kwargs):
            pass

        def classify(self, stream, **kwargs):
            pass

        @classmethod
        def component_classes(cls):
            return {"gpd": seisbench.models.GPD}

    def write_config(*arg, **kwargs):
        path = tmp_path / "pipelines" / "mypipeline" / "myconfig.json"
        with open(path, "w") as f:
            f.write('{"components": {"gpd": "dummy"}}\n')

    with patch(
        "seisbench.cache_root", tmp_path
    ):  # Ensure test does not modify SeisBench cache
        with patch("seisbench.util.download_http") as download_http:
            download_http.side_effect = write_config

            with patch("seisbench.models.GPD.from_pretrained") as gpd_from_pretrained:
                gpd_from_pretrained.return_value = (
                    seisbench.models.GPD()
                )  # Return random GPD instance

                MyPipeline.from_pretrained("myconfig")

                gpd_from_pretrained.assert_called_once_with(
                    "dummy", force=False, wait_for_file=False
                )


def test_recurrent_dropout():
    lstm = CustomLSTM(
        ActivationLSTMCell, 1, 100, bidirectional=True, recurrent_dropout=0.25
    )
    x = torch.rand(100, 5, 1)

    with torch.no_grad():
        y = lstm(x)[0]

    assert y.shape == (100, 5, 200)


def test_dpp_detector():
    model = seisbench.models.DPPDetector(input_channels=3, nclasses=3)

    x = torch.rand(16, 3, 500)
    y = model(x)

    assert y.shape == (16, 3)


def test_dpp_ps():
    model = seisbench.models.DPPPicker("P")

    x = torch.rand(16, 1, 500)
    y = model(x)

    assert y.shape == (16, 500)

    model = seisbench.models.DPPPicker("S")

    x = torch.rand(16, 2, 500)
    y = model(x)

    assert y.shape == (16, 500)


def test_resample():
    # Only tests for correct target frequencies and number of samples, but not for correct content
    t1 = obspy.Trace(np.random.rand(1000), header={"sampling_rate": 100})  # Decimate
    t2 = obspy.Trace(np.random.rand(1000), header={"sampling_rate": 25})  # Unchanged
    t3 = obspy.Trace(np.random.rand(1000), header={"sampling_rate": 40})  # Resample

    s = obspy.Stream([t1, t2, t3])
    seisbench.models.WaveformModel.resample(s, 25)
    assert s[0].stats.sampling_rate == 25
    assert len(s[0]) == 250
    assert s[1].stats.sampling_rate == 25
    assert len(s[1]) == 1000
    assert s[1].stats.sampling_rate == 25
    assert len(s[2]) == 625
