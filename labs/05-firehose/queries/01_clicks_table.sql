-- Lab 5, step 4: a table over the clicks that Firehose delivers.
-- Replace YOUR_BUCKET with the name of your bucket (run echo $BUCKET), in the
-- two places where it appears.
-- In the Athena query editor, choose the workgroup big-data-labs-clicks and
-- the database big_data_labs_clicks, and run ONE statement at a time.

-- Statement 1: Firehose writes the clicks in folders such as clicks/2026/10/10/21/.
-- Partition projection makes the table find them by itself.
CREATE EXTERNAL TABLE clicks (
    event_id     string,
    event_time   string,
    session_id   string,
    customer_id  bigint,
    event_type   string,
    product_id   int,
    product_name string,
    category     string,
    device       string,
    amount       bigint
)
PARTITIONED BY (datehour string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://YOUR_BUCKET/clicks/'
TBLPROPERTIES (
    'projection.enabled' = 'true',
    'projection.datehour.type' = 'date',
    'projection.datehour.format' = 'yyyy/MM/dd/HH',
    'projection.datehour.range' = '2026/01/01/00,NOW',
    'projection.datehour.interval' = '1',
    'projection.datehour.interval.unit' = 'HOURS',
    'storage.location.template' = 's3://YOUR_BUCKET/clicks/${datehour}/'
);
