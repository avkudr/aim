from typing import Iterable, Tuple, List
from typing import TYPE_CHECKING
from collections import namedtuple

from aim.storage.treeutils import encode_tree

from aim.sdk.objects import Image
from aim.sdk.run import Run
from aim.sdk.sequence_collection import SequenceCollection
from aim.sdk.sequence import Sequence
from aim.sdk.uri_service import URIService, generate_resource_path

from aim.web.api.runs.utils import get_run_props, collect_run_streamable_data

if TYPE_CHECKING:
    from aim.sdk import Repo

IndexRange = namedtuple('IndexRange', ['start', 'stop'])


def sliced_img_record(values: Iterable[Image], _slice: slice) -> Iterable[Image]:
    yield from zip(range(_slice.start, _slice.stop, _slice.step), values[_slice])


def img_record_to_encodable(image_record, trace, step):
    img_list = []
    for idx, img in image_record:
        img_dump = img.json()
        image_resource_path = generate_resource_path(trace.values.tree.container, (step, idx, 'data'))
        img_dump['blob_uri'] = URIService.generate_uri(trace.run.hashname, 'seqs', image_resource_path)
        img_dump['index'] = idx
        img_list.append(img_dump)
    return img_list


def get_record_and_index_range(traces: SequenceCollection, trace_cache: dict) -> Tuple[IndexRange, IndexRange]:
    rec_start = None
    rec_stop = -1
    idx_start = 0  # record inner indexing is always sequential
    idx_stop = -1
    for run_trace_collection in traces.iter_runs():
        run = run_trace_collection.run
        run_traces = []
        for trace in run_trace_collection.iter():
            run_traces.append(trace)
            rec_start = min(trace.first_step(), rec_start) if rec_start else trace.first_step()
            rec_stop = max(trace.last_step(), rec_stop)
            idx_stop = max(trace.record_length(), idx_stop)
        trace_cache[run.hashname] = {
            'run': run,
            'traces': run_traces
        }
    return IndexRange(rec_start, rec_stop), IndexRange(idx_start, idx_stop)


def get_trace_info(trace: Sequence, rec_slice: slice, idx_slice: slice) -> dict:
    steps = []
    values = []
    steps_vals = trace.values.items_slice(_slice=rec_slice)
    for step, val in steps_vals:
        steps.append(step)
        values.append(img_record_to_encodable(sliced_img_record(val, idx_slice), trace, step))

    return {
        'trace_name': trace.name,
        'context': trace.context.to_dict(),
        'values': values,
        'iters': steps,
        'epochs': list(trace.epochs.values_slice(_slice=rec_slice)),
        'timestamps': list(trace.timestamps.values_slice(_slice=rec_slice)),
    }


def image_search_result_streamer(traces: SequenceCollection,
                                 rec_range: IndexRange, rec_density: int,
                                 idx_range: IndexRange, idx_density: int):
    record_range_missing = rec_range.start is None or rec_range.stop is None
    index_range_missing = idx_range.start is None or idx_range.stop is None
    run_traces = {}

    trcs_rec_range, trcs_idx_range = IndexRange(None, None), IndexRange(None, None)
    if record_range_missing or index_range_missing:
        trcs_rec_range, trcs_idx_range = get_record_and_index_range(traces, trace_cache=run_traces)

    rec_start = rec_range.start if rec_range.start is not None else trcs_rec_range.start
    rec_stop = rec_range.stop if rec_range.stop is not None else trcs_rec_range.stop
    rec_step = (rec_stop - rec_start) // rec_density or 1

    idx_start = idx_range.start if idx_range.start is not None else trcs_idx_range.start
    idx_stop = idx_range.stop if idx_range.stop is not None else trcs_idx_range.stop
    idx_step = (idx_stop - idx_start) // idx_density or 1

    rec_slice = slice(rec_start, rec_stop, rec_step)
    idx_slice = slice(idx_start, idx_stop, idx_step)

    def pack_run_data(run_: Run, traces_: list, rec_slice: slice, idx_slice: slice):
        run_dict = {
            run_.hashname: {
                'ranges': {
                    'record_range': [rec_slice.start, rec_slice.stop],
                    'index_range': [idx_slice.start, idx_slice.stop],
                    'record_slice': [rec_slice.start, rec_slice.stop, rec_slice.step],
                    'index_slice': [idx_slice.start, idx_slice.stop, idx_slice.step]
                },
                'params': run_.get(...),
                'traces': traces_,
                'props': get_run_props(run_)
            }
        }
        encoded_tree = encode_tree(run_dict)
        return collect_run_streamable_data(encoded_tree)

    if run_traces:
        for run_info in run_traces.values():
            traces_list = []
            for trace in run_info['traces']:
                traces_list.append(get_trace_info(trace, rec_slice, idx_slice))
            yield pack_run_data(run_info['run'], traces_list, rec_slice, idx_slice)
    else:
        for run_trace_collection in traces.iter_runs():
            traces_list = []
            for trace in run_trace_collection.iter():
                traces_list.append(get_trace_info(trace, rec_slice, idx_slice))
            yield pack_run_data(run_trace_collection.run, traces_list, rec_slice, idx_slice)


def images_batch_result_streamer(uri_batch: List[str], repo: 'Repo'):
    uri_service = URIService(repo=repo)
    yield from uri_service.request_batch(uri_batch=uri_batch)
