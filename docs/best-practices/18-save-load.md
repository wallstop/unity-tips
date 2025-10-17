# Save/Load & Data Versioning

Reliable save systems preserve player progress even as your game evolves. Design them with explicit
schemas, versioning, and lightweight serialization to avoid corrupted data or migration bugs.

## Core goals

- **Versioned data** – Include a schema version in every save so you can migrate old data.
- **Deterministic serialization** – Use binary formats for compact, fast saves on all platforms.
- **Crash-safe writes** – Save to a temp file, flush, then atomically replace the main save file.

## Recommended stack: Protobuf

Protocol Buffers (Protobuf) serialize strongly typed data into compact binary blobs. They support
backwards-compatible schema evolution by marking new fields as optional, making them ideal for
long-lived save files.

```proto
syntax = "proto3";

message PlayerData {
  uint32 version = 1;
  uint32 level = 2;
  uint32 experience = 3;
  repeated string unlocked_items = 4;
}
```

- **Unity Helpers integration:** The Wallstop Studios Unity Helpers package ships with Protobuf
  support out of the box—use its serialization helpers to read/write player data without wiring the
  runtime yourself.
- Store serialized blobs in `Application.persistentDataPath` and encrypt or checksum if cheaters are
  a concern.

## Save pipeline

1. Assemble pure data models (no `MonoBehaviour` references) that describe player progress.
2. Serialize to a memory buffer (`MemoryStream` or Unity Helpers wrapper) using Protobuf.
3. Write to disk via a temp file + `File.Replace` (or platform equivalent) to avoid partial writes.
4. Run the entire pipeline on a background thread, then switch back to the main thread before
   touching Unity objects.

## Loading & migrations

- Deserialize into the latest schema. When `save.version < CurrentVersion`, run migration steps to
  add defaults or rename fields before returning data to gameplay.
- Keep migration functions idempotent and covered by automated tests.
- Log any unexpected fields or corrupt blobs for telemetry so you can patch issues quickly.

## Testing strategies

- Add integration tests that create multiple save versions and load them in the latest build.
- Stress test by saving/loading rapidly while toggling app focus to mimic mobile suspends.
- Validate file size and serialization time on mobile/console hardware to avoid noticeable hitches.

A save system built on Protobuf, with Unity Helpers doing the heavy lifting, remains durable across
content updates and platform ports. Invest early so your players never lose progress, even after
months of live updates.
