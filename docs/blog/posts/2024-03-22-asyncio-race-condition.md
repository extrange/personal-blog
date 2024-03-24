---
date: 2024-03-22
categories:
    - Programming
---

# Race conditions with `asyncio` in Python

What do you think the output of the following code will be?

<!-- more -->

```python linenums="1"
import asyncio

async def main():
    ran = False

    async def foo():
        nonlocal ran # Lets us modify from the outer scope

        print(f"{ran=}")

        if not ran:

            # Pretend this is an await for another async function
            await asyncio.sleep(0)

            ran = True
            print("after ran = True")

    async with asyncio.TaskGroup() as tg:
        for _ in range(3):
            tg.create_task(foo())

if __name__ == "__main__":
    asyncio.run(main())
```

We might guess:

```
ran=False
after ran = True
ran=True
ran=True
```

With the explanation being:

-   First, we schedule `should_only_print_once` to run 3 times in the `TaskGroup`.
-   The first time the event loop enters the function, `ran = False` is printed.
-   Since `ran` is `False`, we enter the `if` conditional and set `ran = True`.
-   Print `after ran = True`.
-   For the remaining times the event loop enters the function, `ran` is now `False`. So, we print `ran = False` twice and end.

In fact, the output is:

```
ran=False
ran=False
ran=False
after ran = True
after ran = True
after ran = True
```

What is happening here?

## Asynchronous Execution

At line 13, we have `await asyncio.sleep(0)`.

This _yields_ control flow to the event loop. At this point, the event loop is free to continue executing other tasks, such as the other 2 tasks for `foo()`.

Importantly, at this point, the value of `ran` is still `False` - the initial run has not yet reached `ran = True`. Therefore, when the event loop reenters `foo()` subsequently, it sees that `ran == False`.

Finally, when all 3 asynchronous executions of `foo()` have reached `await asyncio.sleep(0)`, the first one to run sets `ran = True`, and that is what the subsequent executions see and print.

## Fixing the issue

The correct way to fix this is by wrapping code that accesses shared state in an [`asyncio.Lock`][asyncio-lock].

```python linenums="1" hl_lines="5 8"
import asyncio

async def main():
    ran = False
    lock = asyncio.Lock()

    async def foo():
        async with lock:
            nonlocal ran # Lets us modify from the outer scope

            print(f"{ran=}")

            if not ran:

                await asyncio.sleep(0)

                ran = True
                print("after ran = True")

    async with asyncio.TaskGroup() as tg:
        for _ in range(3):
            tg.create_task(foo())

if __name__ == "__main__":
    asyncio.run(main())
```

Output:

```
ran=False
after ran = True
ran=True
ran=True
```

When the first task for `foo()` executes, it acquires the `lock` and gains exclusive access to the subsequent code.

During the `await` at line 8, control flow switches to the other tasks executing `foo()`, but because the lock was already acquired by the first task, they cannot proceed further.

Execution finally returns to the first task, which sets `ran = True` and completes, allowing the rest of the waiting tasks to execute in the same fashion.

[asyncio-lock]: https://docs.python.org/3/library/asyncio-sync.html#lock
