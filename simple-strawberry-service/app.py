import asyncio
import strawberry
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL
from typing import AsyncGenerator
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# Dummy query to satisfy the schema requirement
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "hello world"

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(self) -> AsyncGenerator[int, None]:
        try:
            i = 0
            while True:
                yield i
                print("Iteration number:", i)
                i += 1
                await asyncio.sleep(10000) # Sleep FOREVER
        finally:
            print("Subscription terminated")

schema = strawberry.federation.Schema(query=Query, subscription=Subscription, enable_federation_2=True)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")