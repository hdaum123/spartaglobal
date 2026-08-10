# Splunk Upskilling

# What is Splunk?

- Splunk is a platform used to **collect, search, monitor and analyse machine-generated data**.
- It can be used for security monitoring, IT operations, troubleshooting and data analysis.
- **Splunk Enterprise Security (ES)** is Splunk's SIEM solution.
- Splunk uses **SPL (Search Processing Language)** to search and analyse data.

---

# What Makes Up Splunk?

The main components of Splunk are:

- **Forwarder** → Collects raw logs and forwards them to Splunk.
- **Indexer** → Processes, indexes and stores events.
- **Search Head** → The main interface used to search and analyse data using SPL.

### Basic Flow

`Forwarder → Indexer → Search Head`

## Universal Forwarder

A **Universal Forwarder** is a lightweight agent installed on a system that collects logs and sends them to an Indexer.

It does very little processing itself.

## Heavy Forwarder

A **Heavy Forwarder** can collect and forward data but can also process, filter and route the data before sending it to an Indexer.

**Think:**

`Universal Forwarder = Collect + Send`

`Heavy Forwarder = Process + Send`

---

# Splunk Deployments

Splunk can be deployed in different ways depending on the size of the environment.

### Standalone / Single Instance

One Splunk instance performs multiple roles, such as searching and indexing.

This is normally suitable for smaller environments, testing or learning.

### Basic Deployment

Forwarders can be installed on different machines to collect data and send it back to Splunk.

### Multi-Instance / Distributed

In larger environments, Splunk roles can be separated across multiple systems.

For example:

- **Search Head** → Handles searches and user interaction.
- **Indexer** → Processes and stores data.
- **Forwarder** → Collects and sends data.

This makes Splunk easier to scale when dealing with large amounts of data.

---

# Data Pipeline

The data pipeline explains what happens to data as it travels through Splunk.

`INPUT → Parsing → License Usage → Indexing → Searching`

## Input Phase

The **input phase** is where Splunk first receives the data.

Some common input types include:

- Files and directories
- Forwarders
- TCP/UDP
- HTTP Event Collector (HEC)
- Scripts

Splunk also adds important metadata to the data.

### Source

The **source** identifies the path or location the data came from.

Example:

`/var/log/security.log`

### Host

The **host** identifies the system or device associated with the data.

Example:

`www1`

### Sourcetype

The **sourcetype** describes the format or type of data.

It helps Splunk understand how the data should be interpreted and displayed.

Examples could include:

`access_combined`

`syslog`

Splunk is good at automatically detecting many sourcetypes, but it is important to preview the data and make sure Splunk has selected the correct format.

### Index

The **index** is where Splunk stores and organises the data.

Example:

```spl
index=web
```

---

# Parsing Phase

During parsing, Splunk processes the raw data and starts turning it into individual **events**.

Splunk looks at things such as:

- Where one event ends and another begins
- Timestamps
- Data formatting

---

# Indexing Phase

Once the data has been processed, Splunk:

- Indexes the events
- Compresses the raw data
- Writes the data to disk

The data can then be searched using SPL.

---

# What is an Event?

An **event** is a single record of activity that has happened on a system.

Examples include:

- A successful login
- A failed login
- A website request
- A firewall blocking traffic

Events are what we search and analyse within Splunk.

---

# Data Preview

When adding data:

**Settings → Add Data → Select File**

Before indexing the data, check things such as:

- Timestamp
- Host
- Source
- Sourcetype
- Index
- Field extraction

This is important because the data needs to be interpreted correctly before it is useful for searching.

A useful search for checking ingested data is:

```spl
index=your_index
| stats count BY host sourcetype source
```

This shows how many events are associated with each host, sourcetype and source.

---

# App vs Add-on

Splunk **Apps** and **Add-ons** both extend Splunk, but they have different purposes.

## Add-on

An Add-on normally works in the background and helps Splunk collect and understand data.

It can provide:

- Data inputs
- Parsing
- Field extractions
- Data normalisation

## App

An App normally provides functionality that the user interacts with.

It can contain:

- Dashboards
- Searches
- Reports
- Alerts
- Visualisations

**Think:**

`Add-on = Collect / Prepare`

`App = Display / Analyse`

---

# Module 5 — Basics of Searching

Splunk data is searched using **SPL (Search Processing Language)**.

## Basic Search

```spl
index=web sourcetype="access_combined"
```

**Meaning:** Search the `web` index for events with the `access_combined` sourcetype.

To search an entire index:

```spl
index=web
```

## Search Modes

Splunk provides different search modes.

### Fast

Prioritises speed and does less field discovery.

### Smart

Balances speed and the amount of information returned depending on the type of search.

### Verbose

Returns more event and field information, which can be useful when exploring or investigating data.

---

# Module 6 — Knowledge Objects

A **Knowledge Object (KO)** is a reusable object created in Splunk to make searching, analysing and understanding data easier.

Examples include:

- Saved searches
- Dashboards
- Alerts
- Reports
- Lookups
- Event types
- Tags
- Fields
- Data models

## Dashboard

A **dashboard** displays data visually using things such as charts, graphs, tables and single values.

## Report

A **report** is a saved search that can be run again or scheduled.

## Alert

An **alert** triggers when the results of a search meet a particular condition.

For example, an alert could be created for a high number of failed login attempts.

## Lookup

A **lookup** adds extra information to Splunk events using external/reference data such as a CSV file.

---

# Managing Knowledge Objects

Knowledge Objects can have permissions that control who is allowed to view or edit them.

It is also useful to use a consistent naming convention.

For example:

`group_type_description`

This makes Knowledge Objects easier to identify and manage.

---

# Event Types

An **event type** allows a particular search to be given a name.

For example, a search that finds failed logins could be saved as:

`failed_logins`

When creating an event type, I can provide:

- A name
- A search string
- Permissions

This makes the search easier to identify and reuse later.

---

# Module 7 — Fields

**Fields** are searchable key-value pairs extracted from event data.

For example:

```text
status=200
```

Here:

- `status` = field
- `200` = value

Another example:

```text
src_ip=10.10.10.5
```

Splunk can recognise multiple fields within a single event.

Fields allow searches to become more specific because I can search for a particular field and value rather than searching all of the raw data.

---

# Searching Fields

For example:

```spl
categoryId=sports
```

This searches for events where `categoryId` has the value `sports`.

## Using `!=`

```spl
categoryId!=sports
```

This searches for events where `categoryId` exists but does **not** have the value `sports`.

## Using `NOT`

```spl
NOT categoryId=sports
```

This excludes events containing `categoryId=sports`.

Unlike `!=`, this can also include events where the `categoryId` field does not exist.

This means `!=` and `NOT` can return different results.

---

# Module 8 — SPL Syntax

**SPL (Search Processing Language)** is the language used to search, filter, transform and analyse data in Splunk.

## Common Operators

Some common operators include:

- `AND`
- `OR`
- `NOT`
- `=`
- `!=`
- `>`
- `<`
- `>=`
- `<=`

---

# Understanding SPL Syntax

Splunk colour-codes different parts of an SPL search.

### Blue — Commands

Examples:

- `stats`
- `table`
- `rename`
- `timechart`

### Orange — Keywords / Command Modifiers

Examples:

- `AND`
- `OR`
- `NOT`
- `AS`
- `BY`

### Green — Arguments

Examples:

- `limit`
- `span`

### Purple — Functions

Examples:

- `sum()`
- `min()`
- `max()`
- `values()`
- `tostring()`

---

# Building an SPL Search

A useful way to think about building SPL is:

`Pull Data → Command → Function → Arguments`

For example:

```spl
index=web OR index=security
| stats sum(bytes) AS Total_Bytes
```

Breaking this down:

- `index=web OR index=security` → Gets the data.
- `stats` → Command.
- `sum()` → Function.
- `bytes` → Field being used.
- `AS Total_Bytes` → Renames the result.

---

# Module 8B — Basic SPL Commands

## Table

The `table` command displays specific fields as columns.

```spl
index=web
| table clientip action categoryId status
```

This allows me to focus on the fields I actually want to see.

---

## Rename

The `rename` command changes how a field name appears in the results.

```spl
index=web
| table clientip action categoryId status
| rename action AS "Action"
```

This changes the display name from `action` to `Action`.

---

## Fields

The `fields` command controls which fields are included in the results.

```spl
index=web
| fields clientip action status
```

A field can also be removed:

```spl
index=web
| fields - source
```

---

## Dedup

The `dedup` command removes duplicate results based on a field.

```spl
index=web
| dedup clientip
```

If the same `clientip` appears multiple times, `dedup` can be used to keep one result for each unique value.

---

## Sort

The `sort` command puts results into a particular order.

```spl
index=web
| sort clientip
```

To sort numerical results from highest to lowest:

```spl
index=web
| sort - bytes
```

---

# Combining SPL Commands

SPL becomes more useful when multiple commands are piped together.

For example:

```spl
index=web
| table clientip action categoryId status
| where isnotnull(action)
| rename action AS "Action"
```

This search:

1. Searches the `web` index.
2. Displays selected fields.
3. Only keeps results where `action` has a value.
4. Renames `action` to `Action`.

Another example:

```spl
index=web
| dedup clientip
| table clientip
```

This removes duplicate client IP addresses and displays the unique values.

---

# Key Things I've Learned So Far

- Splunk collects and analyses machine-generated data.
- Forwarders collect data and send it to Splunk.
- Indexers process and store the data.
- Search Heads allow users to search and analyse the data.
- Host, source and sourcetype describe where data came from and what type of data it is.
- Knowledge Objects make searches and analysis reusable.
- Fields are key-value pairs within events.
- SPL is used to search and manipulate Splunk data.
- Pipes allow multiple SPL commands to be combined.
- Commands such as `table`, `fields`, `rename`, `dedup` and `sort` can be used to manipulate search results.