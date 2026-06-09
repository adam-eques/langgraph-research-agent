from __future__ import annotations
import asyncio
from research_agent.stream_writer import StreamWriter, stream_to_string, write_chunks


def test_write_and_read():
    async def run():
        w = StreamWriter()
        await asyncio.gather(
            write_chunks(w, ["Hello, ", "World!"]),
            stream_to_string(w),
        )
        return await stream_to_string(w)

    async def _full():
        w = StreamWriter()
        task = asyncio.create_task(write_chunks(w, ["hello ", "world"]))
        result = await stream_to_string(w)
        await task
        return result

    assert asyncio.run(_full()) == "hello world"


def test_total_written():
    async def run():
        w = StreamWriter()
        await w.write("abc")
        await w.write("de")
        return w.total_written
    assert asyncio.run(run()) == 5


def test_write_after_close_raises():
    async def run():
        w = StreamWriter()
        await w.close()
        try:
            await w.write("x")
            return False
        except RuntimeError:
            return True
    assert asyncio.run(run())
