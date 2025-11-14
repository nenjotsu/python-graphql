from app.api.graphql_schema import schema
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

app = FastAPI()

app.include_router(GraphQLRouter(schema), prefix="/graphql")


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5533)


if __name__ == "__main__":
    main()
