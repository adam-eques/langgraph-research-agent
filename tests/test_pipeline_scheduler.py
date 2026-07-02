from __future__ import annotations
import asyncio
from research_agent.pipeline_scheduler import PipelineScheduler, ScheduleType


def test_register_and_tick():
    counter = {"n": 0}

    async def job():
        counter["n"] += 1

    scheduler = PipelineScheduler()
    scheduler.register("test_job", job, schedule_type=ScheduleType.ONCE)
    ran = asyncio.run(scheduler.tick())
    assert "test_job" in ran and counter["n"] == 1


def test_once_only_runs_once():
    counter = {"n": 0}

    async def job():
        counter["n"] += 1

    scheduler = PipelineScheduler()
    scheduler.register("once_job", job, schedule_type=ScheduleType.ONCE)
    asyncio.run(scheduler.tick())
    asyncio.run(scheduler.tick())
    assert counter["n"] == 1


def test_unregister():
    scheduler = PipelineScheduler()
    scheduler.register("j", lambda: None, schedule_type=ScheduleType.ONCE)
    assert scheduler.unregister("j") is True and len(scheduler.job_names()) == 0
