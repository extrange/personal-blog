---
categories:
    - Programming
date: 2023-09-17
---

# Yjs vs Traditional Databases

[Yjs][yjs] is a [conflict-free, replicated data type][crdt], which allows for distributed, collaborative editing and offline synchronization, with automatic conflict resolution.

It can also be used as a database backend.

Recently, I was deciding between Yjs and the [Prisma][prisma] + [tRPC][trpc] + [SQLite][sqlite] combination. As it was a small todo-style app, I settled on Yjs.

Here are the factors I considered for this decision.

|                     | YJS                                                                                            | tRPC + Prisma + SQLite                                                   |
| ------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Initial Load        | Fast, as client has copy of entire DB and only updates are synced                              | Slow, as entire DB needs to be sent over. Fast, if paginated.            |
| Concurrent edits    | Supported                                                                                      | Not supported                                                            |
| Full-text Search    | Yes, client-side                                                                               | If paginated, server-side (requires PostgresQL). Otherwise, client-side. |
| Auth                | Supported                                                                                      | Supported                                                                |
| Offline Sync        | Yes, with PWA                                                                                  | No                                                                       |
| Enforcing Relations | Difficult (e.g. two users, one deletes the parent, the other deletes the child, and they sync) | Yes                                                                      |
| Enforcing Schema    | Client-side                                                                                    | Server-side                                                              |
| Best use cases      | Small databases                                                                                | Large databases                                                          |

[yjs]: https://github.com/yjs/yjs
[crdt]: https://lars.hupel.info/topics/crdt/01-intro/
[prisma]: https://www.prisma.io/
[sqlite]: https://www.prisma.io/docs/reference/database-reference/database-features
[trpc]: https://trpc.io/
