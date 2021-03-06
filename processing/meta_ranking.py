import asyncio
import multiprocessing
import concurrent.futures

from collections import OrderedDict
from operator import itemgetter
from processing.indexers import *


async def collect_indexes(topic: str) -> list:
    indexers = [CitizendiumIndexer(),
                EveripediaIndexer(),
                InfoPleaseIndexer()]

    tasks = [indexer.index(topic) for indexer in indexers]
    return list(await asyncio.gather(*tasks))


def borda_ranking(indexes: list, max_source_pool: int) -> list:
    agg_rank = []
    total_indexes = sum([len(sublist) for sublist in indexes])

    for sublist in indexes:
        sublen = len(sublist)

        if sublen == 0:
            continue

        weight, ratio = sublist[0]['weight'], sublen / total_indexes
        agg_rank.extend([(index['title'], index['href'], i / sublen * weight * ratio, index['origin'])
                         for i, index in enumerate(sublist[::-1], 1)])

    source_table, source_ranks, source_origins = OrderedDict(), OrderedDict(), OrderedDict()

    for title, href, val, origin in agg_rank:
        if title in source_ranks:
            source_table[title].append((href, val))
            source_ranks[title].append(val)
        else:
            source_table[title] = [(href, val)]
            source_ranks[title] = [val]
            source_origins[title] = origin

    for title, ranks in source_ranks.items():
        _, max_ranked_href = max(enumerate(source_table[title]), key=itemgetter(1))
        source_table[title] = max_ranked_href[0]
        source_ranks[title] = sum(ranks)

    sorted_ranks = dict(sorted(source_ranks.items(),
                               key=lambda item: item[1],
                               reverse=True))

    return [(topic, source_table[topic], source_origins[topic])
            for topic, _
            in list(sorted_ranks.items())[:max_source_pool]]


async def collect_ranked_hrefs(topic: str, max_source_pool: int) -> list:
    loop = asyncio.get_running_loop()

    indexes = await collect_indexes(topic)

    with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as pool:
        ranks = await loop.run_in_executor(pool, borda_ranking, indexes, max_source_pool)

    return ranks
