On Apollo Router 2.4.0, when a client closed a subscription connection with the Router, the Router would then send a `connection_terminate` message to a subgraph, which could handle it, and clean up any resources.

On 2.5.0, when a client closes a subscription connection with the Router, the Router doesn't send the `connection_terminate` message over the websocket to the subgraph.

A fix went out for 2.4.0 that kept subscriptions alive whenever the federated schema was updated, but it seems it inadvertently kept the subscriptions alive when expected terminations take place.

The reason this is a problem is resources on the subgraph are not able to be free'd up, because the subscriptions are kept alive indefinately, which in our case has caused out of memory issues.



The following are steps to reproduce using a simple Strawberry subscription in python, and using rover to run Apollo Router locally:

In `simple-strawberry-service` run:

1. `poetry install`
2. `uvicorn app:app --port 8005 --log-level debug`


In another terminal run in `apollo-router-test` run:

`APOLLO_KEY="YOUR SECRET APOLLO KEY" APOLLO_GRAPH_REF="YOUR FEDERATED GRAPH REF" APOLLO_ROVER_DEV_ROUTER_VERSION=2.4.0 rover dev --supergraph-config supergraph.yaml --router-config router.yaml -l info`


This should run Apollo Router locally and make it accessible at: `http://localhost:8000/graphql`


Then in a third terminal run:

```
curl -N \
  -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Accept: multipart/mixed;boundary=graphql;subscriptionSpec=1.0,application/json" \
  -d '{"query":"subscription { count }"}'
```

To create the subscription with the subgraph.

When you CTRL+C to kill the subscription in 2.4.0, the subscription is gracefully terminated in the `simple-strawberry-service` and you can see the `connection_terminate` message in the console.

However, when you run:

`APOLLO_KEY="YOUR SECRET APOLLO KEY" APOLLO_GRAPH_REF="YOUR FEDERATED GRAPH REF" APOLLO_ROVER_DEV_ROUTER_VERSION=2.5.0 rover dev --supergraph-config supergraph.yaml --router-config router.yaml -l info`

with 2.5.0, the `connection_terminate` message is never received, and the subscription with `simple-strawberry-service` is never terminated. Create multiple subscriptions over time... and memory begins to leak because they are never terminated.



