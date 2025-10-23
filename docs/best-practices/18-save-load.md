# Save/Load & Data Versioning

Reliable save systems preserve player progress even as your game evolves. Design them with explicit
schemas, versioning, and lightweight serialization to avoid corrupted data or migration bugs.

## Core goals

- **Versioned data** – Include a schema version in every save so you can migrate old data.
- **Deterministic serialization** – Use binary formats for compact, fast saves on all platforms.
- **Crash-safe writes** – Save to a temp file, flush, then atomically replace the main save file.

## Recommended stack: protobuf-net attributes

`protobuf-net` delivers compact, deterministic binary serialization while letting you author the
schema with familiar C# attributes. That keeps the entire save definition inside Unity and avoids
the fragile tooling required to compile `.proto` message files.

```csharp
using ProtoBuf;

[ProtoContract]
public sealed class PlayerSave
{
    public const int CurrentVersion = 3;

    [ProtoMember(1)]
    public int Version { get; set; } = CurrentVersion;

    [ProtoMember(2)]
    public int Level { get; set; }

    [ProtoMember(3)]
    public int Experience { get; set; }

    [ProtoMember(4)]
    public List<string> UnlockedItems { get; set; } = new();
}
```

- Annotate plain data containers (`[ProtoContract]`, `[ProtoMember]`) and let `protobuf-net` handle
  the wire format.
- Skip `.proto` sources entirely—no generated classes, no extra build steps, and fewer CI failures.
- Store serialized blobs in `Application.persistentDataPath` and encrypt or checksum if cheaters are
  a concern.
- The Wallstop Studios Unity Helpers package already references `protobuf-net`; plug your attribute
  models into its helper methods instead of wiring Protobuf runtimes manually.

> **Important:** Do not author `.proto` message files for Unity saves. Attribute-driven models keep
> serialization predictable without the fragile build steps those messages require.

## JSON for simple or player-facing data

Lightweight JSON files shine when designers or power users need to read or tweak data. Keep them for
non-critical settings such as graphics options, photo mode presets, or tutorial flags.

- Leverage `System.Text.Json` or `Newtonsoft.Json` for human-readable saves that require zero build
  tooling.
- Expect malformed edits—wrap loads in try/catch, validate the shape, and fall back to defaults when
  the file is missing or corrupt.
- Sign or hash the payload before trusting it in competitive games; plain JSON invites tampering.
- Document which keys are safe to touch in modding guides so you can triage bug reports quickly.

```csharp
using System.IO;
using System.Text.Json;
using UnityEngine;

public sealed class UserSettings
{
    public float MasterVolume { get; set; } = 0.8f;
    public bool Subtitles { get; set; } = true;
}

public static class SettingsStorage
{
    private static readonly string Path =
        Path.Combine(Application.persistentDataPath, "settings.json");

    public static UserSettings LoadOrDefaults()
    {
        if (!File.Exists(Path))
        {
            return new UserSettings();
        }

        try
        {
            var json = File.ReadAllText(Path);
            return JsonSerializer.Deserialize<UserSettings>(json) ?? new UserSettings();
        }
        catch (JsonException)
        {
            Debug.LogWarning("Settings JSON invalid; reverting to defaults.");
            return new UserSettings();
        }
    }
}
```

## Save pipeline

1. Assemble pure data models (no `MonoBehaviour` references) that describe player progress.
1. Serialize to a memory buffer (`MemoryStream` or Unity Helpers wrapper) using
   `Serializer.Serialize`.
1. Write to disk via a temp file + `File.Replace` (or platform equivalent) to avoid partial writes.
1. Run the entire pipeline on a background thread, then switch back to the main thread before
   touching Unity objects.

```csharp
using System.IO;
using ProtoBuf;
using UnityEngine;

public static class SaveSystem
{
    private static readonly string SavePath =
        Path.Combine(Application.persistentDataPath, "player.bin");

    public static void Save(PlayerSave data)
    {
        var tempPath = SavePath + ".tmp";

        using (var file = File.Create(tempPath))
        {
            Serializer.Serialize(file, data);
            file.Flush(true);
        }

        File.Replace(tempPath, SavePath, backupFileName: null);
    }

    public static PlayerSave LoadOrCreate()
    {
        if (!File.Exists(SavePath))
        {
            return new PlayerSave();
        }

        using var file = File.OpenRead(SavePath);
        return Serializer.Deserialize<PlayerSave>(file);
    }
}
```

- Keep member numbers sequential. When you add a new field, assign the next number and leave earlier
  numbers untouched to remain compatible with old saves.
- Run migrations on the loaded `PlayerSave` object before exposing it to gameplay systems.

## Loading & migrations

- Deserialize into the latest schema. When `save.Version < PlayerSave.CurrentVersion`, run migration
  steps to add defaults or rename fields before returning data to gameplay.
- Keep migration functions idempotent and covered by automated tests.
- Log any unexpected fields or corrupt blobs for telemetry so you can patch issues quickly.

## SQLite for transactional or replayable data

When you must persist a history of events—crafting transactions, mail, combat logs, or economy
counters—use a lightweight SQLite database. It offers ACID guarantees, query flexibility, and
incremental updates without rewriting an entire save blob.

- Use `sqlite-net` or `Mono.Data.Sqlite` and locate the database under
  `Application.persistentDataPath`.
- Encapsulate writes in transactions so crashes never leave partial changes on disk.
- Partition tables by system (`inventory_transactions`, `mail_messages`) and keep schema migrations
  alongside your C# migrations.
- Vacuum rarely to avoid frame spikes; schedule it on the main menu or background screens.

```csharp
using Mono.Data.Sqlite;

using (var connection = new SqliteConnection($"Data Source={dbPath};Version=3;"))
{
    connection.Open();

    using var tx = connection.BeginTransaction();
    using var cmd = connection.CreateCommand();
    cmd.CommandText =
        "INSERT INTO inventory_transactions (player_id, item_id, delta) VALUES (@p, @i, @d)";
    cmd.Parameters.AddWithValue("@p", playerId);
    cmd.Parameters.AddWithValue("@i", itemId);
    cmd.Parameters.AddWithValue("@d", change);
    cmd.ExecuteNonQuery();
    tx.Commit();
}
```

## Testing strategies

- Add integration tests that create multiple save versions and load them in the latest build.
- Stress test by saving/loading rapidly while toggling app focus to mimic mobile suspends.
- Validate file size and serialization time on mobile/console hardware to avoid noticeable hitches.

A save system built on attribute-driven `protobuf-net` contracts keeps schema evolution inside your
C# assemblies, avoids fragile Proto message generation, and remains durable across content updates.
Invest early so your players never lose progress, even after months of live updates.
