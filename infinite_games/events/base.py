
import asyncio
import bittensor as bt
from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any, Callable, Dict, Optional


@dataclass
class Submission:
    """Miner submission data"""

    submitted_ts: int
    answer: float


class EventStatus:
    """Generic event status"""
    DISCARDED = 1
    PENDING = 2
    SETTLED = 3
    # In case of errors
    NOT_IMPLEMENTED = 4


@dataclass
class ProviderEvent:
    event_id: str
    event_type: str
    description: str
    starts: datetime
    resolve_date: datetime
    answer: Optional[int]
    local_updated_at: datetime
    status: EventStatus
    miner_predictions: Dict[int, Submission]
    metadata: Dict[str, Any]


class EventProvider:

    def __init__(self) -> None:
        self.registered_events: Dict[str, ProviderEvent] = {

        }
        # This hook called both when refetching events from provider
        self.event_update_hook_fn: Optional[Callable[[ProviderEvent], None]] = None
        self.listen_delay_seconds = 5
        # loop = asyncio.get_event_loop()
        # loop.create_task(self._listen_events())

    async def sync_events():
        raise NotImplemented()

    async def listen_events(self):
        """In base implementation we try to update each registered event via get_single_event"""
        while True:
            bt.logging.info(f'Update events: {len(self.registered_events.items())}')
            for event_id, event_data in self.registered_events.items():
                if event_data.status == EventStatus.PENDING:
                    # TODO: Add support for id_in query depending on provider, azuro supports that
                    event_data: ProviderEvent = await self.get_single_event(event_data.event_id)
                    self.update_event(event_data.event_id, event_data.description, event_data.starts,
                                      event_data.status, event_data.resolve_date, event_data.metadata)
            await asyncio.sleep(self.listen_delay_seconds)

    async def get_single_event(event_id) -> ProviderEvent:
        raise NotImplemented()

    async def event_subscribe():
        raise NotImplemented()

    async def is_event_resolved(event_id):
        raise NotImplemented()

    def event_key(self, event_id):
        return f'{self.__class__.__name__}-{event_id}'

    def register_event(self, event_id, description, 
                       start_time, event_status,
                       resolve_time=None, answer=None, metadata=None):
        """Adds or updates event. Returns true - if this event not in the list yet"""
        if self.registered_events.get(self.event_key(event_id)):
            # Naive event update
            self.update_event(event_id, description, start_time, event_status, resolve_time, answer, metadata)

        self.registered_events[self.event_key(event_id)] = ProviderEvent(
            event_id,
            self.__class__.__name__,
            description,
            start_time,
            resolve_time,
            None,
            datetime.now(),
            event_status,
            self.registered_events.get(self.event_key(event_id), {}).get('miner_predictions', []),
            metadata,
        )

        return True

    def update_event(self, event_id, description,
                     start_time, event_status,
                     resolve_time=None, answer=None,  metadata=None):
        """Updates event"""

        if not self.registered_events.get(self.event_key(event_id)):
            bt.logging.error(f'No event found in registry {self.__class__.__name__} {event_id}!')
            return False
        self.registered_events[self.event_key(event_id)] = ProviderEvent(
            event_id,
            self.__class__.__name__,
            description,
            start_time,
            resolve_time,
            answer,
            datetime.now(),
            event_status,
            self.registered_events[self.event_key(event_id)].miner_predictions,
            metadata,
        )
        if self.event_update_hook_fn and callable(self.event_update_hook_fn):
            self.event_update_hook_fn(self.registered_events.get(self.event_key(event_id)))

        return True

    def on_event_updated_hook(self, event_update_hook_fn: Callable[[ProviderEvent], None]):
        """Depending on provider, hook that will be called when we have updates for registered events"""
        self.event_update_hook_fn = event_update_hook_fn

    def get_event(self, event_id):
        return self.registered_events.get(self.get_event_key(event_id))

    async def save_state(self):
        with open('event_state.json', 'w') as f:
            json.dump(self.registered_events, f)

    async def load_state(self):
        self.registered_events = json.load(open('event_state.json', 'r'))

    async def get_miner_prediction(self, uid: int, event_id: str) -> Optional[Submission]:
        submission = self.registered_events.get(self.event_key(event_id), {}).get(uid)
        return Submission(
            submitted_ts=submission.get('submitted_ts'),
            answer=submission.get('answer'),
        )

    async def miner_predict(self, uid: int, event_id: str, answer: float) -> Submission:
        event = self.registered_events.get(self.event_key(event_id))
        if not event:
            bt.logging.warning(f'Event {event_id} was not found in registered events while submitting {uid=} answer {answer}!')
            return False
        submission: Submission = event['miner_predictions'].get(uid)

        if submission:
            bt.logging.info(f'Overriding miner {uid=} submission for {event_id=} from {submission.answer} to {answer}')
        new_submission = Submission(
            submitted_ts=datetime.now().timestamp(),
            answer=answer,
        )
        event['miner_predictions'][uid] = new_submission
        return submission
