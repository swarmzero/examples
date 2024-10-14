import asyncio

from dotenv import load_dotenv

from app import livepeer_swarm


load_dotenv()


async def main():
    print(
        "Welcome to the Livepeer Youtube Video Generator Swarm!\nVisit https://SwarmZero.ai to learn more.\n\nType "
        "'exit' to quit.\n"
    )

    while True:
        prompt = input("\n\nEnter your prompt: \n\n")
        if prompt.lower() == "exit":
            break
        response = await livepeer_swarm.chat(prompt)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
