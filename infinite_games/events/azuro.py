
import backoff
import bittensor as bt

import asyncio
from datetime import datetime
import json
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import websockets

from infinite_games.azurodictionaries.outcomes import OUTCOMES

from infinite_games.events.base import EventProvider, EventStatus, ProviderEvent


class AzuroEventProvider(EventProvider):
    def __init__(self) -> None:
        super().__init__()
        self.transport = AIOHTTPTransport(
            url="https://thegraph.azuro.org/subgraphs/name/azuro-protocol/azuro-api-gnosis-v3"
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)

        self._listen_stream_url = 'wss://streams.azuro.org/v1/streams/conditions'
        # self.ws_connection = None
        # asyncio.create_task()

    def convert_status(self, azuro_status):
        return {
            'Created': EventStatus.PENDING,
            'Resolved': EventStatus.SETTLED,
            'Canceled': EventStatus.DISCARDED,
            'Paused': EventStatus.PENDING
        }.get(azuro_status, EventStatus.PENDING)

    async def on_update(self, ws):
        try:
            async for message in ws:
                print(message)
        except websockets.ConnectionClosed:
            self.ws_connection = None

    async def subscribe_to_condition(self, cids=[]):
        if self.ws_connection:
            if cids:
                self.ws_connection.send(json.dumps(
                    {
                        "action": 'subscribe',
                        "conditionIds": cids,
                    }
                ))
            else:
                bt.logging.warning('Azuro: Empty CID passed for ws subscribe')
        else:
            bt.logging.error('Azuro: Could not subscribe to event no WS connection found!')

    async def listen_for_updates(self):
        async for websocket in websockets.connect(
            self._listen_stream_url
        ):
            self.ws_connection = websocket
            asyncio.create_task(self.on_update(self, websocket))

    @backoff.on_exception(backoff.expo, Exception, max_time=300)
    async def get_single_event(self, event_id) -> ProviderEvent:
        query = gql(
            """
            query SingleOutcome($id: ID!) {
                outcome(id: $id) {
                    id
                    outcomeId
                    fund
                    result
                    currentOdds
                    condition {
                        id
                        conditionId
                        outcomes {
                            id
                        }
                        status
                        provider
                        game {
                            title
                            gameId
                            slug
                            startsAt
                            league {
                            name
                            slug
                            country {
                                name
                                slug
                            }
                            }
                            status
                            sport {
                            name
                            slug
                            }
                            participants {
                            image
                            name
                            }
                        }
                    }
                }
                }


        """
        )

        async with self.client as session:

            result = await session.execute(
                query,
                {
                    "id": event_id
                }
            )
        if not result:
            bt.logging.error(f'Azuro: Could not fetch event by id  {event_id}')
            return None
        outcome = result['outcome']

        if not outcome:
            bt.logging.error(f'Azuro: Could not fetch event by id  {event_id}')
            return None
        condition = outcome['condition']
        game = condition['game']
        start_date = datetime.fromtimestamp(int(game["startsAt"]))
        event_status = condition.get('status')
        pe = ProviderEvent(
            event_id,
            self.__class__.__name__,
            game.get('title') + ' ,' + OUTCOMES[outcome['outcomeId']].get('_comment'),
            start_date,
            None,
            datetime.now(),
            self.convert_status(event_status),
            None,
            None,
            {
                'conditionId': condition['conditionId'],
                'slug': game.get('slug'),
                'league': game.get('league')
            }
        )
        return pe

    @backoff.on_exception(backoff.expo, Exception, max_time=300)
    async def sync_events(self, start_from: int = None):
        bt.logging.info(f"Azuro: syncing events.. {start_from=} ")
        if not start_from:
            start_from = int(datetime.now().timestamp())

        query = gql(
            """
            query Games($where: Game_filter!, $start: Int!, $per_page: Int!) {
                games(
                    skip: $start
                    first: $per_page
                    where: $where
                    orderBy: startsAt
                    orderDirection: asc
                    subgraphError: allow
                ) {
                    gameId
                    title
                    slug
                    status
                    startsAt
                    league {
                        name
                        slug
                        country {
                            name
                            slug
                        }
                    }
                    sport {
                        name
                        slug
                    }
                    participants {
                        image
                        name
                    }
                    conditions {
                        conditionId                   
                        isExpressForbidden
                        status
                        outcomes {
                            id
                            currentOdds
                            outcomeId
                            result
                        }
                    }
                }
            }


        """
        )

        async with self.client as session:
            result = await session.execute(
                query,
                {
                    "where": {
                        "status": "Created",
                        "hasActiveConditions": True,
                        "startsAt_gt": start_from
                    },
                    "start": 0, "per_page": 10
                },
            )
        for game in result["games"]:
            start_date = datetime.fromtimestamp(int(game["startsAt"]))
            if not game.get('startsAt'):
                bt.logging.warning(f"Azuro game {game.get('slug')} doesnt have start time, skipping..")
                continue
            for condition in game['conditions']:
                event_status = condition.get('status')
                # if not event_status != 'Canceled':
                #     bt.logging.debug(f"Azuro condition for game {game.get('slug')} condition id {condition.get('conditionId')} is {condition.get('status')}, skipping..")
                #     continue

                for outcome in condition['outcomes']:
                    if outcome.get('id') is None:
                        bt.logging.error(f"{game.get('slug')} cid: {condition.get('conditionId')} outcome {outcome.get('outcomeId')} does not have id, skip..")
                        continue
                    if outcome.get('result') is not None:
                        bt.logging.debug(f"{game.get('slug')} cid: {condition.get('conditionId')} outcome {outcome.get('outcomeId')} resolved, skipping..")
                        continue

                    self.register_event(
                        outcome.get('id'),
                        game.get('title') + ' ,' + OUTCOMES[outcome['outcomeId']].get('_comment'),
                        start_date,
                        event_status=self.convert_status(event_status),
                        resolve_time=None,
                        answer=outcome['result'],
                        metadata={
                            'conditionId': condition['conditionId'],
                            'slug': game.get('slug'),
                            'league': game.get('league')
                        }
                    )

                self.subscribe_to_condition(condition.get('conditionId'))