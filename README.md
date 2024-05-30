# format_vicente_batch_processing
An idea to make vicente's batching process more efficient.

### Preliminary idea

If, after mapping its header fields, it does not contain the same ones as the reference header, we discard the file and report exactly what is missing.

Otherwise, fields that are not needed are eliminated and rearranged for a more comfortable reading.
